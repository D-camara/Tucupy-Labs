from __future__ import annotations

# Views responsáveis pelo fluxo de créditos e marketplace:
# - Listagem do marketplace (apenas listagens ativas)
# - Detalhe do crédito
# - Criação de crédito (apenas produtor)
# - Ação de listar um crédito para venda (apenas produtor e dono)

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
        return (
            CreditListing.objects.select_related("credit", "credit__owner")
            .filter(is_active=True, credit__status=CarbonCredit.Status.LISTED)
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
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona para a página de detalhe após criar
        return reverse("credit_detail", args=[self.object.pk])


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
            # Regras de prevenção: status deve estar AVAILABLE e não pode haver listagem ativa
            if credit.status != CarbonCredit.Status.AVAILABLE:
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
                return redirect("credit_detail", pk=credit.pk)
    else:
        form = CreditListingForm()

    return render(request, "credits/list_for_sale.html", {"form": form, "credit": credit})


