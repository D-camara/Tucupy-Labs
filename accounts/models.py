from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        PRODUCER = "PRODUCER", _("Producer")
        COMPANY = "COMPANY", _("Company")
        ADMIN = "ADMIN", _("Admin")

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.COMPANY)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.username


class Profile(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="profile")
    company_name = models.CharField(max_length=255, blank=True)
    farm_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Profile<{self.user.username}>"

