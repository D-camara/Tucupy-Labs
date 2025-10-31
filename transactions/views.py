"""Views para transações de compra/venda de créditos."""

from __future__ import annotations

import json
import time
from decimal import Decimal
from typing import Iterator

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.views import company_required
from credits.models import CarbonCredit, CreditListing

from .models import Transaction as TransactionModel


@require_http_methods(["POST"])
@company_required
def buy_credit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View de compra de crédito (Company-only).
    
    Fluxo:
    1. Valida que o crédito existe e está LISTED
    2. Verifica saldo suficiente
    3. Cria transação com status COMPLETED
    4. Deduz saldo do comprador
    5. Adiciona saldo ao vendedor
    6. Transfere propriedade do crédito
    7. Atualiza status do crédito para SOLD
    8. Desativa o listing
    
    Tudo em transação atômica para garantir consistência e evitar race conditions.
    """
    # Executar tudo em transação atômica com SELECT FOR UPDATE
    with transaction.atomic():
        # SELECT FOR UPDATE previne race conditions
        credit = get_object_or_404(
            CarbonCredit.objects.select_for_update(),
            pk=pk
        )
        
        # Validações
        if credit.status != CarbonCredit.Status.LISTED:
            messages.error(request, "Este crédito não está disponível para compra.")
            return redirect("credits:credit_detail", pk=pk)
        
        # Validar que o crédito foi aprovado por um auditor
        if credit.validation_status != CarbonCredit.ValidationStatus.APPROVED:
            messages.error(
                request, 
                "⚠️ Este crédito ainda não foi aprovado por um auditor e não pode ser comprado. "
                "Aguarde a validação para realizar a compra."
            )
            return redirect("credits:credit_detail", pk=pk)
        
        # Buscar listing ativo
        try:
            listing = CreditListing.objects.get(credit=credit, is_active=True)
        except CreditListing.DoesNotExist:
            messages.error(request, "Não foi encontrada uma listagem ativa para este crédito.")
            return redirect("credits:credit_detail", pk=pk)
        
        # Validar que o comprador não é o dono
        if credit.owner == request.user:
            messages.error(request, "Você não pode comprar seu próprio crédito.")
            return redirect("credits:credit_detail", pk=pk)
        
        # Calcular valor total
        total_price = credit.amount * listing.price_per_unit
        
        # Verificar saldo do comprador
        buyer_profile = request.user.profile
        if not buyer_profile.can_buy(total_price):
            messages.error(
                request, 
                f"Saldo insuficiente. Você tem R$ {buyer_profile.balance:.2f}, "
                f"mas precisa de R$ {total_price:.2f}."
            )
            return redirect("credits:credit_detail", pk=pk)
        
        # Criar transação
        txn = TransactionModel.objects.create(
            buyer=request.user,
            seller=credit.owner,
            credit=credit,
            amount=credit.amount,
            total_price=total_price,
            status=TransactionModel.Status.COMPLETED,
        )
        
        # Desativar listing ANTES de mudar status (validação não permite salvar listing de crédito SOLD)
        listing.is_active = False
        listing.save()
        
        # Processar pagamento (deduzir do comprador, adicionar ao vendedor)
        buyer_profile.deduct_balance(total_price)
        credit.owner.profile.add_balance(total_price)
        
        # Transferir propriedade
        credit.owner = request.user
        credit.status = CarbonCredit.Status.SOLD
        credit.save()
    
    messages.success(
        request,
        f"✅ Crédito adquirido com sucesso! Transação #{txn.id} concluída. "
        f"Total: R$ {txn.total_price:.2f} | Saldo restante: R$ {request.user.profile.balance:.2f}"
    )
    return redirect("transactions:transaction_history")


@login_required
def transaction_history(request: HttpRequest) -> HttpResponse:
    """
    View de histórico de transações do usuário.

    Mostra tanto compras quanto vendas do usuário logado,
    ordenadas por data (mais recente primeiro).
    """
    user = request.user

    # Buscar compras e vendas do usuário
    purchases = TransactionModel.objects.filter(buyer=user)
    sales = TransactionModel.objects.filter(seller=user)

    # Combinar e ordenar por timestamp
    all_transactions = (purchases | sales).distinct().order_by("-timestamp")

    context = {
        "transactions": all_transactions,
        "total_purchases": purchases.count(),
        "total_sales": sales.count(),
    }

    return render(request, "transactions/history.html", context)


def public_transactions_view(request: HttpRequest) -> HttpResponse:
    """
    Public-facing view showing recent completed transactions.

    No authentication required. Displays last 10 COMPLETED transactions
    with anonymized participant info (roles only, no personal data).
    """
    transactions = TransactionModel.objects.filter(
        status=TransactionModel.Status.COMPLETED
    ).select_related("buyer", "seller", "credit").order_by("-timestamp")[:10]

    context = {
        "transactions": transactions,
    }

    return render(request, "transactions/public_transactions.html", context)


def _get_client_ip(request: HttpRequest) -> str:
    """Extract client IP from request, considering proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _sse_event_stream(client_ip: str, rate_limit_key: str, session_key: str) -> Iterator[str]:
    """
    Generator for SSE events streaming new completed transactions.

    Polls DB every 2s for new transactions, sends heartbeat every 30s.
    Uses Django cache to track last seen transaction timestamp per client.
    """
    # Send immediate connection confirmation to trigger onopen quickly
    yield ": connected\n\n"

    cache_key = f"sse_last_txn_{client_ip}"
    heartbeat_interval = 30  # seconds
    poll_interval = 2  # seconds
    refresh_interval = 10  # seconds - refresh both rate limit and session
    last_heartbeat = time.time()
    last_refresh = time.time()

    # Get initial last transaction timestamp
    last_txn_time = cache.get(cache_key)
    if not last_txn_time:
        # First connection - get most recent transaction time
        latest_txn = TransactionModel.objects.filter(
            status=TransactionModel.Status.COMPLETED
        ).order_by("-timestamp").first()
        last_txn_time = latest_txn.timestamp if latest_txn else timezone.now()
        cache.set(cache_key, last_txn_time, timeout=3600)  # 1 hour

    try:
        while True:
            current_time = time.time()

            # Send heartbeat to keep connection alive
            if current_time - last_heartbeat >= heartbeat_interval:
                yield ": heartbeat\n\n"
                last_heartbeat = current_time

            # Refresh both rate limit and session to keep them active
            if current_time - last_refresh >= refresh_interval:
                cache.set(rate_limit_key, True, timeout=30)
                # Extend session timeout to allow reconnections
                session_data = cache.get(session_key)
                if session_data:
                    cache.set(session_key, session_data, timeout=60)
                last_refresh = current_time

            # Check for new transactions since last check
            new_transactions = TransactionModel.objects.filter(
                status=TransactionModel.Status.COMPLETED,
                timestamp__gt=last_txn_time
            ).select_related("buyer", "seller", "credit").order_by("timestamp")

            if new_transactions.exists():
                for txn in new_transactions:
                    # Build anonymized transaction data
                    data = {
                        "id": txn.id,
                        "timestamp": txn.timestamp.isoformat(),
                        "buyer_role": txn.buyer.get_role_display(),
                        "seller_role": txn.seller.get_role_display(),
                        "amount": str(txn.amount),
                        "total_price": str(txn.total_price),
                        "credit_origin": txn.credit.origin,
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    last_txn_time = txn.timestamp

                # Update cache with latest transaction time
                cache.set(cache_key, last_txn_time, timeout=3600)

            # Sleep before next poll
            time.sleep(poll_interval)

    except GeneratorExit:
        # Client disconnected - cleanup
        pass


@never_cache
def public_transactions_sse(request: HttpRequest) -> HttpResponse:
    """
    SSE endpoint for real-time transaction updates.

    Implements smart rate limiting with session-based reconnection:
    - Clients get a session ID on first connection (stored in localStorage)
    - Reconnections within 60s with valid session ID bypass rate limit
    - Prevents abuse while allowing legitimate page refreshes
    """
    client_ip = _get_client_ip(request)
    session_id = request.GET.get('session_id', '')

    rate_limit_key = f"sse_active_{client_ip}"
    session_key = f"sse_session_{session_id}" if session_id else None

    # Check if this is a valid reconnection
    is_valid_reconnection = False
    if session_key and cache.get(session_key):
        is_valid_reconnection = True
        # Clean up old rate limit to allow reconnection
        cache.delete(rate_limit_key)

    # Check if client already has an active connection (rate limiting)
    if cache.get(rate_limit_key) and not is_valid_reconnection:
        return HttpResponse(
            "Too many connections. Only 1 SSE connection per IP allowed.",
            status=429,
            content_type="text/plain"
        )

    # Generate new session ID if not reconnecting
    if not is_valid_reconnection:
        import uuid
        session_id = str(uuid.uuid4())
        session_key = f"sse_session_{session_id}"

    # Mark connection as active
    cache.set(rate_limit_key, True, timeout=5)
    # Store session with 60s timeout (allows reconnections within this window)
    cache.set(session_key, {'ip': client_ip, 'connected_at': time.time()}, timeout=60)

    def event_stream_wrapper():
        """Wrapper to ensure cache cleanup and send session ID."""
        try:
            # Send session ID to client on connection
            yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"
            # Stream transaction updates
            yield from _sse_event_stream(client_ip, rate_limit_key, session_key)
        finally:
            # Clean up rate limit on disconnect
            cache.delete(rate_limit_key)
            # Keep session alive for 60s to allow reconnection

    response = StreamingHttpResponse(
        event_stream_wrapper(),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Disable nginx buffering
    return response