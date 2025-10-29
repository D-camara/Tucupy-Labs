from __future__ import annotations

from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    buyer = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="purchases")
    seller = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="sales")
    credit = models.ForeignKey("credits.CarbonCredit", on_delete=models.PROTECT, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Txn<{self.id}> {self.status}"

