from __future__ import annotations

from typing import Optional, Callable, cast

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django import forms  # usado apenas para tipagem no form_valid

from .models import User, Profile
from .forms import RegistrationForm, ProfileForm


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
    template_name = "register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Conta criada com sucesso. Bem-vindo(a) ao EcoTrade!")
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = "login.html"
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("accounts:login")


class ProfileView(LoginRequiredMixin, UpdateView):
    """Editar o perfil do usuário autenticado."""
    model = Profile
    form_class = ProfileForm
    template_name = "profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None) -> Profile:
        # Garante que o usuário sempre edite o próprio perfil
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return super().form_valid(form)


# Healthcheck simples
def placeholder(_request: HttpRequest) -> HttpResponse:  # Simple placeholder view for wiring tests
    return HttpResponse("accounts ok")
