from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        PRODUCER = "PRODUCER", _("Producer")
        COMPANY = "COMPANY", _("Company")
        ADMIN = "ADMIN", _("Admin")

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


# Criação automática de Profile para cada User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created: bool, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # garante que o perfil exista
        Profile.objects.get_or_create(user=instance)
