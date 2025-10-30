"""Views para transações de compra/venda de créditos."""

from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    2. Cria transação com status COMPLETED
    3. Transfere propriedade do crédito
    4. Atualiza status do crédito para SOLD
    5. Desativa o listing
    
    Tudo em transação atômica para garantir consistência.
    """
    credit = get_object_or_404(CarbonCredit, pk=pk)
    
    # Validações
    if credit.status != CarbonCredit.Status.LISTED:
        messages.error(request, "Este crédito não está disponível para compra.")
        return redirect("credit_detail", pk=pk)
    
    # Buscar listing ativo
    try:
        listing = CreditListing.objects.get(credit=credit, is_active=True)
    except CreditListing.DoesNotExist:
        messages.error(request, "Não foi encontrada uma listagem ativa para este crédito.")
        return redirect("credit_detail", pk=pk)
    
    # Validar que o comprador não é o dono
    if credit.owner == request.user:
        messages.error(request, "Você não pode comprar seu próprio crédito.")
        return redirect("credit_detail", pk=pk)
    
    # Executar compra em transação atômica
    with transaction.atomic():
        # Criar transação
        txn = TransactionModel.objects.create(
            buyer=request.user,
            seller=credit.owner,
            credit=credit,
            amount=credit.amount,
            total_price=credit.amount * listing.price_per_unit,
            status=TransactionModel.Status.COMPLETED,
        )
        
        # Transferir propriedade
        credit.owner = request.user
        credit.status = CarbonCredit.Status.SOLD
        credit.save()
        
        # Desativar listing
        listing.is_active = False
        listing.save()
    
    messages.success(
        request,
        f"Crédito adquirido com sucesso! Transação #{txn.id} concluída. "
        f"Total: R$ {txn.total_price:.2f}"
    )
    return redirect("transaction_history")


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