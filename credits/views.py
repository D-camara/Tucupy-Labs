from __future__ import annotations

# Views responsáveis pelo fluxo de créditos e marketplace:
# - Listagem do marketplace (apenas listagens ativas)
# - Detalhe do crédito
# - Criação de crédito (apenas produtor)
# - Ação de listar um crédito para venda (apenas produtor e dono)

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from accounts.models import User
from .forms import CarbonCreditForm, CreditListingForm
from .models import CarbonCredit, CreditListing


class ProducerRequiredMixin:
    """Mixin para restringir acesso a usuários com papel de PRODUTOR.

    Esta verificação complementa o LoginRequiredMixin quando usado em conjunto.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Se não estiver autenticado, negar (LoginRequiredMixin normalmente redirecionaria)
            raise PermissionDenied("Autenticação necessária")
        if getattr(request.user, "role", None) != User.Roles.PRODUCER:
            raise PermissionDenied("Permissão negada: apenas produtores")
        return super().dispatch(request, *args, **kwargs)


class MarketplaceListView(ListView):
    """Página do marketplace: mostra apenas listagens ativas de créditos LISTED.

    Paginação: 10 itens por página.
    """

    model = CreditListing
    template_name = "credits/marketplace.html"
    context_object_name = "listings"
    paginate_by = 10

    def get_queryset(self):
        # select_related otimiza joins para acessar credit e owner sem múltiplas queries
        # Apenas créditos aprovados por auditor aparecem no marketplace
        return (
            CreditListing.objects.select_related("credit", "credit__owner")
            .filter(
                is_active=True,
                credit__status=CarbonCredit.Status.LISTED,
                credit__validation_status=CarbonCredit.ValidationStatus.APPROVED
            )
            .order_by("-listed_at")
        )


class CreditDetailView(DetailView):
    """Detalhe de um crédito específico.

    Também injeta no contexto as listagens ativas desse crédito e um formulário
    de listagem (usado quando o dono produtor quiser listar).
    """

    model = CarbonCredit
    template_name = "credits/detail.html"
    context_object_name = "credit"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Listagens ativas vinculadas a este crédito
        ctx["active_listings"] = self.object.listings.filter(is_active=True)
        # Formulário para listar este crédito (aparece para o dono produtor)
        ctx["listing_form"] = CreditListingForm()
        return ctx


class CreditCreateView(LoginRequiredMixin, ProducerRequiredMixin, CreateView):
    """Tela de criação de crédito (restrita a produtores autenticados)."""

    model = CarbonCredit
    form_class = CarbonCreditForm
    template_name = "credits/create.html"

    def form_valid(self, form: CarbonCreditForm):
        # Define o dono do crédito como o usuário logado
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # Mensagem informando que o crédito precisa ser aprovado
        messages.success(
            self.request,
            "Crédito criado com sucesso! Ele será revisado por um auditor antes de poder ser listado no marketplace."
        )
        return response

    def get_success_url(self):
        # Redireciona para a página de detalhe após criar
        return reverse("credits:credit_detail", args=[self.object.pk])


@login_required
def list_for_sale(request, pk: int):
    """Ação para listar um crédito para venda.

    Regras:
    - Apenas o dono do crédito, com papel PRODUCER, pode listar
    - Não permite múltiplas listagens ativas para o mesmo crédito
    - Altera o status do crédito para LISTED dentro de uma transação atômica
    """

    credit = get_object_or_404(CarbonCredit, pk=pk)

    # Garantir que apenas o produtor dono do crédito possa listar
    if getattr(request.user, "role", None) != User.Roles.PRODUCER or credit.owner_id != request.user.id:
        raise PermissionDenied("Apenas o produtor dono pode listar este crédito")

    if request.method == "POST":
        form = CreditListingForm(request.POST)
        if form.is_valid():
            # Regras de prevenção: deve estar aprovado, status AVAILABLE, e sem listagem ativa
            if credit.validation_status != CarbonCredit.ValidationStatus.APPROVED:
                form.add_error(None, "Este crédito precisa ser aprovado por um auditor antes de ser listado.")
            elif credit.status != CarbonCredit.Status.AVAILABLE:
                form.add_error(None, "Este crédito não está disponível para listagem.")
            elif credit.listings.filter(is_active=True).exists():
                form.add_error(None, "Já existe uma listagem ativa para este crédito.")
            else:
                # Atualizações sensíveis feitas dentro de uma transação para consistência
                with transaction.atomic():
                    listing = form.save(commit=False)
                    listing.credit = credit
                    listing.is_active = True
                    listing.save()
                    # Marca o crédito como LISTED
                    credit.status = CarbonCredit.Status.LISTED
                    credit.save(update_fields=["status"])
                return redirect("credits:credit_detail", pk=credit.pk)
    else:
        form = CreditListingForm()

    return render(request, "credits/list_for_sale.html", {"form": form, "credit": credit})


def credit_history(request, pk: int):
    """
    View pública do histórico de propriedade (blockchain-style).

    Mostra timeline completa de ownership desde a criação até o estado atual.
    Acessível por qualquer usuário (não requer autenticação) para transparência.
    """
    credit = get_object_or_404(CarbonCredit, pk=pk)

    # Buscar todo o histórico ordenado por timestamp
    history = credit.ownership_history.select_related(
        'from_owner', 'to_owner', 'transaction'
    ).all()

    context = {
        'credit': credit,
        'history': history,
        'total_transfers': history.count(),
    }

    return render(request, "credits/history.html", context)


# =========================
# AUDITOR VIEWS
# =========================

@login_required
def auditor_dashboard(request):
    """Dashboard para auditores visualizarem créditos para validação."""
    if request.user.role != User.Roles.AUDITOR:
        raise PermissionDenied("Acesso restrito a auditores")
    
    # Determina a aba atual
    current_tab = request.GET.get('tab', 'pending')
    
    # Filtra créditos baseado na aba
    if current_tab == 'pending':
        credits = CarbonCredit.objects.filter(
            validation_status=CarbonCredit.ValidationStatus.PENDING
        ).select_related('owner', 'validated_by').order_by('-created_at')
    elif current_tab == 'under_review':
        # Mostra apenas créditos em análise pelo auditor atual
        credits = CarbonCredit.objects.filter(
            validation_status=CarbonCredit.ValidationStatus.UNDER_REVIEW,
            validated_by=request.user
        ).select_related('owner', 'validated_by').order_by('-created_at')
    else:  # history
        credits = CarbonCredit.objects.filter(
            validated_by=request.user
        ).exclude(
            validation_status=CarbonCredit.ValidationStatus.PENDING
        ).select_related('owner').order_by('-validated_at')
    
    # Estatísticas
    context = {
        'current_tab': current_tab,
        'credits': credits,
        'pending_count': CarbonCredit.objects.filter(
            validation_status=CarbonCredit.ValidationStatus.PENDING
        ).count(),
        'under_review_count': CarbonCredit.objects.filter(
            validation_status=CarbonCredit.ValidationStatus.UNDER_REVIEW,
            validated_by=request.user
        ).count(),
        'approved_by_me_count': CarbonCredit.objects.filter(
            validated_by=request.user,
            validation_status=CarbonCredit.ValidationStatus.APPROVED
        ).count(),
        'rejected_by_me_count': CarbonCredit.objects.filter(
            validated_by=request.user,
            validation_status=CarbonCredit.ValidationStatus.REJECTED
        ).count(),
    }
    
    return render(request, "credits/auditor_dashboard.html", context)


@login_required
def review_credit(request, pk):
    """View para revisar e validar um crédito específico."""
    if request.user.role != User.Roles.AUDITOR:
        raise PermissionDenied("Acesso restrito a auditores")
    
    credit = get_object_or_404(CarbonCredit, pk=pk)
    
    # Se o crédito já foi revisado por outro auditor, apenas mostrar
    if credit.validation_status in [CarbonCredit.ValidationStatus.APPROVED, 
                                     CarbonCredit.ValidationStatus.REJECTED]:
        if credit.validated_by != request.user:
            from django.contrib import messages
            messages.info(request, f"Este crédito já foi validado por {credit.validated_by.username}")
    
    if request.method == "POST":
        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()
        
        from django.contrib import messages
        from accounts.emails import send_credit_validation_result
        
        if action == 'start_review':
            credit.start_review(request.user)
            messages.success(request, "✅ Você marcou este crédito como 'Em Análise'")
            
        elif action == 'approve':
            if not notes:
                messages.error(request, "❌ Adicione observações sobre a aprovação")
                return render(request, "credits/review_credit.html", {'credit': credit})
            
            credit.approve_validation(request.user, notes)
            
            # Envia email ao produtor
            try:
                send_credit_validation_result(
                    producer_email=credit.owner.email,
                    producer_name=credit.owner.get_full_name() or credit.owner.username,
                    credit_title=f"{credit.amount} {credit.unit} - {credit.origin}",
                    approved=True,
                    auditor_notes=notes
                )
            except Exception as e:
                messages.warning(request, f"⚠️ Crédito aprovado, mas erro ao enviar email: {str(e)}")
            
            messages.success(request, f"✅ Crédito #{credit.id} aprovado com sucesso!")
            return redirect('credits:auditor_dashboard')
            
        elif action == 'reject':
            if not notes:
                messages.error(request, "❌ Você deve explicar o motivo da rejeição")
                return render(request, "credits/review_credit.html", {'credit': credit})
            
            credit.reject_validation(request.user, notes)
            
            # Envia email ao produtor
            try:
                send_credit_validation_result(
                    producer_email=credit.owner.email,
                    producer_name=credit.owner.get_full_name() or credit.owner.username,
                    credit_title=f"{credit.amount} {credit.unit} - {credit.origin}",
                    approved=False,
                    auditor_notes=notes
                )
            except Exception as e:
                messages.warning(request, f"⚠️ Crédito rejeitado, mas erro ao enviar email: {str(e)}")
            
            messages.success(request, f"✅ Crédito #{credit.id} rejeitado. Produtor será notificado.")
            return redirect('credits:auditor_dashboard')
    
    return render(request, "credits/review_credit.html", {'credit': credit})


@login_required
def view_credit(request, pk):
    """View simples para visualizar detalhes de um crédito."""
    credit = get_object_or_404(CarbonCredit, pk=pk)
    return render(request, "credits/view_credit.html", {'credit': credit})


