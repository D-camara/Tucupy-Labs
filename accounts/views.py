from __future__ import annotations

from typing import Optional, Callable, cast
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django import forms  # usado apenas para tipagem no form_valid

from .models import User, Profile
from .forms import RegistrationForm, ProfileForm, CustomLoginForm


# =========================
# RBAC Mixins / Decorators
# =========================

class RoleRequiredMixin(UserPassesTestMixin):
    """Use em CBVs. Ex.: class MinhaView(ProducerRequiredMixin, ...)"""
    required_role: Optional[str] = None

    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        if not user.is_authenticated:
            return False
        if self.required_role is None:
            return True
        return user.role == self.required_role


class ProducerRequiredMixin(RoleRequiredMixin):
    required_role = User.Roles.PRODUCER


class CompanyRequiredMixin(RoleRequiredMixin):
    required_role = User.Roles.COMPANY


# Decorators para FBVs
def producer_required(view_func: Callable[..., HttpResponse]):
    decorated = login_required(
        user_passes_test(lambda u: cast(User, u).role == User.Roles.PRODUCER)(view_func)
    )
    return decorated


def company_required(view_func: Callable[..., HttpResponse]):
    decorated = login_required(
        user_passes_test(lambda u: cast(User, u).role == User.Roles.COMPANY)(view_func)
    )
    return decorated


# =========
# Views
# =========

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        user = form.save()
        login(self.request, user)
        role_name = "Produtor" if user.role == User.Roles.PRODUCER else "Empresa"
        messages.success(
            self.request, 
            f"🎉 Conta criada com sucesso! Bem-vindo(a) ao Tucupi Labs, {user.username}! Você está registrado como {role_name}."
        )
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        """Adiciona mensagem de erro amigável."""
        messages.error(self.request, "Nome de usuário ou senha incorretos. Verifique e tente novamente.")
        return super().form_invalid(form)


class LogoutView(DjangoLogoutView):
    """View de logout que aceita GET e POST."""
    next_page = reverse_lazy("dashboard:index")
    http_method_names = ['get', 'post', 'options']
    
    def dispatch(self, request, *args, **kwargs):
        """Adiciona mensagem de logout antes de deslogar."""
        if request.user.is_authenticated:
            username = request.user.username
            response = super().dispatch(request, *args, **kwargs)
            messages.success(request, f"👋 Até logo, {username}! Você saiu da sua conta com sucesso.")
            return response
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Permite logout via GET (mais user-friendly)."""
        return self.post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    """Editar o perfil do usuário autenticado."""
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None) -> Profile:
        # Garante que o usuário sempre edite o próprio perfil
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return super().form_valid(form)


@login_required
@company_required
def add_balance_view(request: HttpRequest) -> HttpResponse:
    """View para empresas adicionarem saldo à conta."""
    user = cast(User, request.user)
    
    if request.method == "POST":
        amount_str = request.POST.get("amount", "").strip()
        
        if not amount_str:
            messages.error(request, "❌ Por favor, informe o valor a adicionar.")
            return render(request, "accounts/add_balance.html", {"current_balance": user.profile.balance})
        
        try:
            amount = Decimal(amount_str)
            
            if amount <= 0:
                messages.error(request, "❌ O valor deve ser maior que zero.")
                return render(request, "accounts/add_balance.html", {"current_balance": user.profile.balance})
            
            if amount > Decimal("1000000"):
                messages.error(request, "❌ Valor muito alto. Máximo permitido: R$ 1.000.000,00")
                return render(request, "accounts/add_balance.html", {"current_balance": user.profile.balance})
            
            # Adicionar saldo
            old_balance = user.profile.balance
            user.profile.add_balance(amount)
            new_balance = user.profile.balance
            
            messages.success(
                request,
                f"✅ Saldo adicionado com sucesso! "
                f"R$ {old_balance:.2f} + R$ {amount:.2f} = R$ {new_balance:.2f}"
            )
            return redirect("dashboard:index")
            
        except (InvalidOperation, ValueError):
            messages.error(request, "❌ Valor inválido. Use apenas números (ex: 1000.50)")
            return render(request, "accounts/add_balance.html", {"current_balance": user.profile.balance})
    
    # GET
    return render(request, "accounts/add_balance.html", {"current_balance": user.profile.balance})


# Healthcheck simples
def placeholder(_request: HttpRequest) -> HttpResponse:  # Simple placeholder view for wiring tests
    return HttpResponse("accounts ok")
