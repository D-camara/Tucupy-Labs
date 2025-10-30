from __future__ import annotations

from typing import Optional, Callable, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import User
from .forms import AuditorRegistrationForm
# ========= RBAC genérico =========
class RoleRequiredMixin(UserPassesTestMixin):
    required_role: Optional[str] = None

    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        if not user.is_authenticated:
            return False
        if self.required_role is None:
            return True
        return user.role == self.required_role

# ---- Producer ----
class ProducerRequiredMixin(RoleRequiredMixin):
    required_role = User.Roles.PRODUCER

def producer_required(view_func: Callable[..., HttpResponse]):
    return login_required(
        user_passes_test(lambda u: cast(User, u).is_authenticated and u.role == User.Roles.PRODUCER)(view_func)
    )

# ---- Company ----
class CompanyRequiredMixin(RoleRequiredMixin):
    required_role = User.Roles.COMPANY

def company_required(view_func: Callable[..., HttpResponse]):
    return login_required(
        user_passes_test(lambda u: cast(User, u).is_authenticated and u.role == User.Roles.COMPANY)(view_func)
    )

# ---- Auditor (precisa estar aprovado: is_active=True) ----
class AuditorRequiredMixin(RoleRequiredMixin):
    required_role = User.Roles.AUDITOR

    def test_func(self) -> bool:
        user = cast(User, self.request.user)
        return user.is_authenticated and user.role == User.Roles.AUDITOR and user.is_active

def auditor_required(view_func: Callable[..., HttpResponse]):
    return login_required(
        user_passes_test(lambda u: cast(User, u).is_authenticated and u.role == User.Roles.AUDITOR and u.is_active)(view_func)
    )

# ========= Auth =========
class LoginView(DjangoLoginView):
    # Sem subpasta, compatível com sua estrutura: accounts/templates/login.html
    template_name = "login.html"
    redirect_authenticated_user = True

class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("accounts:login")

# ========= Cadastro (página principal) =========
class RegisterView(TemplateView):
    """
    Página principal de cadastro (apenas renderiza 'register.html').
    Use essa página para links/CTA para o cadastro de Auditor e/ou outros tipos.
    """
    template_name = "register.html"

# ========= Cadastro de Auditor (com formulário) =========
class AuditorRegisterView(FormView):
    # Sem subpasta, para bater com: accounts/templates/auditor_register.html
    template_name = "auditor_register.html"
    form_class = AuditorRegistrationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form: AuditorRegistrationForm) -> HttpResponse:
        form.save()  # cria User(role=AUDITOR, is_active=False) + AuditorProfile
        messages.success(self.request, "Cadastro enviado. Aguarde aprovação do administrador.")
        return super().form_valid(form)

# ========= Health =========
def placeholder(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("accounts ok")


