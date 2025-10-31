from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    class Roles(models.TextChoices):
        PRODUCER = "PRODUCER", _("Producer")
        COMPANY = "COMPANY", _("Company")
        AUDITOR = "AUDITOR", _("Auditor")
        ADMIN = "ADMIN", _("Admin")

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.COMPANY)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    # Aprovação de acesso (Admin controla)
    approved_at = models.DateTimeField(null=True, blank=True)

    # Helpers
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

@receiver(post_save, sender=User)
def ensure_auditor_profile(sender, instance: User, created: bool, **kwargs):
    """Garante que todo AUDITOR tenha um AuditorProfile (mínimo) após criação."""
    if not created:
        return
    if instance.role == User.Roles.AUDITOR:
        AuditorProfile.objects.get_or_create(
            user=instance, defaults={"full_name": instance.get_full_name() or instance.username}
        )



