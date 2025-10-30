"""Models para transações de compra/venda de créditos de carbono."""

from __future__ import annotations

from django.db import models


class Transaction(models.Model):
    """
    Modelo de transação entre comprador (Company) e vendedor (Producer).
    
    Representa a compra/venda completa de um crédito de carbono.
    Quando status=COMPLETED, a propriedade do crédito foi transferida.
    """
    
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        COMPLETED = "COMPLETED", "Concluída"
        CANCELLED = "CANCELLED", "Cancelada"

    buyer = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="purchases",
        verbose_name="Comprador"
    )
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="sales",
        verbose_name="Vendedor"
    )
    credit = models.ForeignKey(
        "credits.CarbonCredit",
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Crédito"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Quantidade (tCO₂e)"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora"
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status"
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    def __str__(self) -> str:
        return f"Txn#{self.id} - {self.buyer.username} ← {self.seller.username} ({self.status})"



