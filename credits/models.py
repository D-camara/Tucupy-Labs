from __future__ import annotations

from django.db import models


class CarbonCredit(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        LISTED = "LISTED", "Listed"
        SOLD = "SOLD", "Sold"

    owner = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="credits")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    origin = models.CharField(max_length=255)
    generation_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.AVAILABLE)
    unit = models.CharField(max_length=32, default="tons CO2")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Credit<{self.id}> {self.amount} {self.unit}"


class CreditListing(models.Model):
    credit = models.ForeignKey("credits.CarbonCredit", on_delete=models.CASCADE, related_name="listings")
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    listed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Listing<{self.id}> for Credit<{self.credit_id}>"

