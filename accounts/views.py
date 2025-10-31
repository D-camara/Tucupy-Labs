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
            f"🎉 Conta criada com sucesso! Bem-vindo(a) ao Tucupy Labs, {user.username}! Você está registrado como {role_name}."
        )
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self) -> str:
        """Redireciona para o dashboard após login bem-sucedido."""
        return reverse_lazy("dashboard:index")
    
    def form_invalid(self, form):
        """Adiciona mensagem de erro amigável."""
        messages.error(self.request, "Nome de usuário ou senha incorretos. Verifique e tente novamente.")
        return super().form_invalid(form)


class LogoutView(DjangoLogoutView):
    """View de logout que aceita GET e POST."""
    next_page = reverse_lazy("dashboard:landing")  # Redireciona para landing page, não login
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


# =========================
# AUDITOR APPLICATION
# =========================

def auditor_application_view(request: HttpRequest) -> HttpResponse:
    """View para candidatura de auditor - cria usuário E candidatura ao mesmo tempo."""
    from .forms import AuditorRegistrationForm
    from .models import AuditorApplication
    from .emails import send_auditor_application_confirmation, send_admin_new_application_notification
    
    # Se já está logado, redireciona
    if request.user.is_authenticated:
        user = cast(User, request.user)
        
        # Verifica se já é auditor ou admin
        if user.role in [User.Roles.AUDITOR, User.Roles.ADMIN]:
            messages.info(request, "ℹ️ Você já possui um perfil de auditor.")
            return redirect("dashboard:index")
        
        # Verifica se já tem candidatura pendente
        existing_application = AuditorApplication.objects.filter(
            user=user,
            status=AuditorApplication.Status.PENDING
        ).first()
        
        if existing_application:
            messages.warning(request, "⚠️ Você já possui uma candidatura pendente. Aguarde a análise.")
            return redirect("dashboard:index")
        
        # Se já tem conta mas não é auditor, mostra mensagem
        messages.info(request, "ℹ️ Você já possui uma conta. A candidatura de auditor é feita em um formulário separado.")
        return redirect("dashboard:index")
    
    if request.method == "POST":
        form = AuditorRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            user = form.save()
            
            # NÃO faz login automático - usuário só entra após aprovação
            # login(request, user)  # REMOVIDO: auditor deve ser aprovado primeiro
            
            # Pega a candidatura recém-criada
            application = AuditorApplication.objects.get(user=user)
            
            # Envia email de confirmação ao candidato
            print(f"\n🔵 [DEBUG] Tentando enviar email para: {application.email}")
            print(f"🔵 [DEBUG] Nome do candidato: {application.full_name}")
            
            try:
                result = send_auditor_application_confirmation(
                    user_email=application.email,
                    user_name=application.full_name
                )
                print(f"✅ [DEBUG] Email enviado com sucesso! Resultado: {result}")
            except Exception as e:
                print(f"❌ [DEBUG] ERRO ao enviar email: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.warning(
                    request,
                    f"⚠️ Candidatura enviada, mas houve erro ao enviar email de confirmação: {str(e)}"
                )
            
            # Notifica administradores
            try:
                admin_emails = list(
                    User.objects.filter(role=User.Roles.ADMIN, is_active=True)
                    .values_list('email', flat=True)
                )
                if admin_emails:
                    send_admin_new_application_notification(
                        admin_emails=admin_emails,
                        applicant_name=application.full_name,
                        applicant_email=application.email,
                        application_id=application.pk
                    )
            except Exception as e:
                # Não bloqueia o fluxo se falhar
                pass
            
            messages.success(
                request,
                "✅ Candidatura enviada com sucesso! Você receberá um email quando for aprovado. "
                "Após a aprovação, você poderá fazer login com suas credenciais."
            )
            return redirect("accounts:login")
    else:
        form = AuditorRegistrationForm()
    
    return render(request, "accounts/auditor_application_new.html", {"form": form})


# =========================
# ADMIN DASHBOARD
# =========================

@login_required
def admin_dashboard_view(request: HttpRequest) -> HttpResponse:
    """Dashboard administrativo para gerenciar candidaturas e usuários."""
    from django.db.models import Count, Q
    from .models import AuditorApplication
    from credits.models import CarbonCredit
    from transactions.models import Transaction
    
    user = cast(User, request.user)
    
    # Verifica se é admin (superuser ou role ADMIN)
    if not user.is_admin:
        messages.error(request, "❌ Acesso negado. Apenas administradores podem acessar esta página.")
        return redirect("dashboard:index")
    
    # Candidaturas pendentes
    pending_applications = AuditorApplication.objects.filter(
        status=AuditorApplication.Status.PENDING
    ).select_related('user').order_by('-created_at')
    
    # Todas as candidaturas (para histórico)
    all_applications = AuditorApplication.objects.select_related(
        'user', 'reviewed_by'
    ).order_by('-created_at')[:50]
    
    # Estatísticas gerais
    stats = {
        'total_users': User.objects.count(),
        'total_producers': User.objects.filter(role=User.Roles.PRODUCER).count(),
        'total_companies': User.objects.filter(role=User.Roles.COMPANY).count(),
        'total_auditors': User.objects.filter(role=User.Roles.AUDITOR).count(),
        'pending_applications': pending_applications.count(),
        'approved_applications': AuditorApplication.objects.filter(status=AuditorApplication.Status.APPROVED).count(),
        'rejected_applications': AuditorApplication.objects.filter(status=AuditorApplication.Status.REJECTED).count(),
        'total_credits': CarbonCredit.objects.count(),
        'pending_validation': CarbonCredit.objects.filter(validation_status='PENDING').count(),
        'approved_credits': CarbonCredit.objects.filter(validation_status='APPROVED').count(),
        'total_transactions': Transaction.objects.filter(status='COMPLETED').count(),
    }
    
    # Usuários recentes
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'pending_applications': pending_applications,
        'all_applications': all_applications,
        'stats': stats,
        'recent_users': recent_users,
    }
    
    return render(request, "accounts/admin_dashboard.html", context)


@login_required
def approve_auditor_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Aprova candidatura de auditor."""
    from .models import AuditorApplication
    from .emails import send_auditor_approval_notification
    
    user = cast(User, request.user)
    
    # Verifica se é admin (superuser ou role ADMIN)
    if not user.is_admin:
        messages.error(request, "❌ Acesso negado.")
        return redirect("dashboard:index")
    
    try:
        application = AuditorApplication.objects.get(pk=pk)
    except AuditorApplication.DoesNotExist:
        messages.error(request, "❌ Candidatura não encontrada.")
        return redirect("accounts:admin_dashboard")
    
    if application.status != AuditorApplication.Status.PENDING:
        messages.warning(request, f"⚠️ Esta candidatura já foi {application.get_status_display().lower()}.")
        return redirect("accounts:admin_dashboard")
    
    # Aprova candidatura
    application.approve(user)
    
    # Envia email
    try:
        send_auditor_approval_notification(
            user_email=application.email,
            user_name=application.full_name
        )
    except Exception as e:
        messages.warning(request, f"⚠️ Candidatura aprovada, mas erro ao enviar email: {str(e)}")
    
    messages.success(
        request,
        f"✅ Candidatura de {application.full_name} aprovada! O usuário agora é um auditor."
    )
    
    return redirect("accounts:admin_dashboard")


@login_required
def reject_auditor_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Rejeita candidatura de auditor."""
    from .models import AuditorApplication
    from .emails import send_auditor_rejection_notification
    
    user = cast(User, request.user)
    
    # Verifica se é admin (superuser ou role ADMIN)
    if not user.is_admin:
        messages.error(request, "❌ Acesso negado.")
        return redirect("dashboard:index")
    
    try:
        application = AuditorApplication.objects.get(pk=pk)
    except AuditorApplication.DoesNotExist:
        messages.error(request, "❌ Candidatura não encontrada.")
        return redirect("accounts:admin_dashboard")
    
    if application.status != AuditorApplication.Status.PENDING:
        messages.warning(request, f"⚠️ Esta candidatura já foi {application.get_status_display().lower()}.")
        return redirect("accounts:admin_dashboard")
    
    if request.method == "POST":
        reason = request.POST.get("reason", "Candidatura não atende aos requisitos mínimos.")
        
        # Rejeita candidatura
        application.reject(user, reason)
        
        # Envia email
        try:
            send_auditor_rejection_notification(
                user_email=application.email,
                user_name=application.full_name,
                reason=reason
            )
        except Exception as e:
            messages.warning(request, f"⚠️ Candidatura rejeitada, mas erro ao enviar email: {str(e)}")
        
        messages.success(
            request,
            f"✅ Candidatura de {application.full_name} rejeitada."
        )
        
        return redirect("accounts:admin_dashboard")
    
    return render(request, "accounts/reject_auditor.html", {"application": application})


# Healthcheck simples
def placeholder(_request: HttpRequest) -> HttpResponse:  # Simple placeholder view for wiring tests
    return HttpResponse("accounts ok")
