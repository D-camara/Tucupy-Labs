from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        PRODUCER = "PRODUCER", _("Produtor")
        COMPANY = "COMPANY", _("Empresa")
        AUDITOR = "AUDITOR", _("Auditor")
        ADMIN = "ADMIN", _("Administrador")

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.COMPANY)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    # Helpers para RBAC simples
    @property
    def is_producer(self) -> bool:
        return self.role == self.Roles.PRODUCER

    @property
    def is_company(self) -> bool:
        return self.role == self.Roles.COMPANY

    @property
    def is_auditor(self) -> bool:
        return self.role == self.Roles.AUDITOR

    @property
    def is_admin(self) -> bool:
        """Retorna True se o usuário é admin (superuser ou role ADMIN)"""
        return self.is_superuser or self.role == self.Roles.ADMIN

    @property
    def is_approved(self) -> bool:
        # Por padrão usamos is_active para o gate de login.
        return bool(self.is_active)

    def approve(self):
        """Aprova o usuário para acesso (Admin)."""
        if not self.is_active:
            self.is_active = True
            self.approved_at = timezone.now()
            self.save(update_fields=["is_active", "approved_at"])

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.username


class Profile(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="profile")
    company_name = models.CharField(max_length=255, blank=True)
    farm_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Saldo virtual para compra de créditos (R$)"
    )

    def can_buy(self, amount):
        """Verifica se tem saldo suficiente para comprar."""
        return self.balance >= amount
    
    def add_balance(self, amount):
        """Adiciona saldo à carteira."""
        self.balance += amount
        self.save()
    
    def deduct_balance(self, amount):
        """Deduz saldo da carteira."""
        if not self.can_buy(amount):
            raise ValueError("Saldo insuficiente")
        self.balance -= amount
        self.save()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Profile<{self.user.username}>"


class AuditorProfile(models.Model):
    """Perfil específico para Auditor, preenchido no cadastro."""
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="auditor_profile")
    full_name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True)
    document_id = models.CharField(max_length=100, blank=True, help_text="Documento/Registro do auditor")
    phone = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"AuditorProfile<{self.user.username}>"


# Criação automática de Profile para cada User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created: bool, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
        # Se é superuser, automaticamente torna ADMIN
        if instance.is_superuser and instance.role != User.Roles.ADMIN:
            instance.role = User.Roles.ADMIN
            instance.save(update_fields=['role'])
        
        # Se é AUDITOR, cria AuditorProfile
        if instance.role == User.Roles.AUDITOR:
            AuditorProfile.objects.get_or_create(
                user=instance, 
                defaults={"full_name": instance.get_full_name() or instance.username}
            )
    else:
        # Garante que o perfil exista
        Profile.objects.get_or_create(user=instance)
        
        # Se virou superuser, torna ADMIN
        if instance.is_superuser and instance.role != User.Roles.ADMIN:
            instance.role = User.Roles.ADMIN
            instance.save(update_fields=['role'])


class AuditorApplication(models.Model):
    """
    Modelo para candidaturas de auditores.
    
    Usuários podem se candidatar para se tornar auditores certificados.
    Admins revisam e aprovam/rejeitam as candidaturas.
    """
    
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pendente")
        APPROVED = "APPROVED", _("Aprovada")
        REJECTED = "REJECTED", _("Rejeitada")
    
    # Candidato
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="auditor_applications",
        verbose_name=_("Usuário")
    )
    
    # Dados do candidato
    full_name = models.CharField(
        max_length=255,
        verbose_name=_("Nome Completo"),
        default=""
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        default=""
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Telefone"),
        help_text=_("Formato: (XX) XXXXX-XXXX")
    )
    organization = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Organização"),
        help_text=_("Empresa ou autônomo")
    )
    linkedin_url = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn"),
        help_text=_("URL do perfil do LinkedIn")
    )
    
    # Arquivos
    certificate = models.FileField(
        upload_to="auditor_applications/certificates/%Y/%m/",
        verbose_name=_("Certificado"),
        help_text=_("Certificado de qualificação (PDF ou imagem)"),
        blank=True
    )
    resume = models.FileField(
        upload_to="auditor_applications/resumes/%Y/%m/",
        blank=True,
        verbose_name=_("Currículo"),
        help_text=_("Currículo em PDF (opcional)")
    )
    
    # Justificativa (motivação)
    justification = models.TextField(
        verbose_name=_("Motivação"),
        help_text=_("Por que você quer ser um auditor na EcoTrade?")
    )
    
    # Aceite dos termos
    terms_accepted = models.BooleanField(
        default=False,
        verbose_name=_("Aceite dos Termos"),
        help_text=_("Li e aceito os termos de auditoria")
    )
    
    # Status da candidatura
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status")
    )
    
    # Datas
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Candidatura")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Revisão")
    )
    
    # Revisor (admin que aprovou/rejeitou)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
        verbose_name=_("Revisado por")
    )
    
    # Motivo da rejeição (opcional)
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_("Motivo da Rejeição"),
        help_text=_("Explique o motivo da rejeição (opcional)")
    )
    
    class Meta:
        verbose_name = _("Candidatura de Auditor")
        verbose_name_plural = _("Candidaturas de Auditores")
        ordering = ["-created_at"]
        # Um usuário pode ter apenas uma candidatura pendente por vez
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_application_per_user"
            )
        ]
    
    def __str__(self) -> str:
        return f"Candidatura de {self.user.username} - {self.get_status_display()}"
    
    def approve(self, admin_user: User) -> None:
        """
        Aprova a candidatura e torna o usuário um auditor.
        
        Args:
            admin_user: Admin que está aprovando
        """
        from django.utils import timezone
        
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        
        # Promove o usuário para AUDITOR e ATIVA a conta
        self.user.role = User.Roles.AUDITOR
        self.user.is_active = True  # ATIVA o usuário
        self.user.save()
    
    def reject(self, admin_user: User, reason: str = "") -> None:
        """
        Rejeita a candidatura.
        
        Args:
            admin_user: Admin que está rejeitando
            reason: Motivo da rejeição
        """
        from django.utils import timezone
        
        self.status = self.Status.REJECTED
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.rejection_reason = reason
        self.save()
