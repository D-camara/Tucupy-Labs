from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CarbonCreditManager(models.Manager):
    """Manager que filtra créditos deletados (soft delete)."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


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
    unit = models.CharField(max_length=32, default="tons CO2")
    auditor_notes = models.TextField(blank=True, default="", help_text="Notas do auditor sobre a validação do crédito")  # ✅ ADICIONAR
    is_verified = models.BooleanField(default=False, help_text="Crédito verificado por administrador")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.AVAILABLE)
    unit = models.CharField(max_length=32, default="tons CO2")
    is_verified = models.BooleanField(default=False, help_text="Crédito verificado por administrador")
    is_deleted = models.BooleanField(default=False, help_text="Soft delete - crédito imutável")

    # Managers
    objects = CarbonCreditManager()  # Filtra deletados por padrão
    objects_all = models.Manager()   # Inclui deletados (para admin)

    def clean(self):
        """Validações de negócio."""
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({"amount": "A quantidade deve ser maior que zero."})
        
        # Converte string para date se necessário (útil em testes)
        from datetime import date
        gen_date = self.generation_date
        if isinstance(gen_date, str):
            from datetime import datetime
            gen_date = datetime.strptime(gen_date, '%Y-%m-%d').date()
        
        if gen_date and gen_date > timezone.now().date():
            raise ValidationError({"generation_date": "A data de geração não pode ser no futuro."})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Soft delete - marca como deletado sem remover do banco (imutabilidade)."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def hard_delete(self):
        """Deleção real (apenas para admin se necessário)."""
        super().delete()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Credit<{self.id}> {self.amount} {self.unit}"


class CreditListing(models.Model):
    credit = models.ForeignKey("credits.CarbonCredit", on_delete=models.CASCADE, related_name="listings")
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    listed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        """Validações de negócio."""
        if self.price_per_unit is not None and self.price_per_unit <= 0:
            raise ValidationError({"price_per_unit": "O preço deve ser maior que zero."})

        # Só valida status se já tem um credit_id (objeto salvo)
        if self.credit_id:
            try:
                if self.credit.status == 'SOLD':
                    raise ValidationError("Não é possível listar um crédito já vendido.")
            except CarbonCredit.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Listing<{self.id}> for Credit<{self.credit_id}>"


class CreditOwnershipHistory(models.Model):
    """Registro imutável de histórico de propriedade (blockchain-style audit trail)."""

    class TransferType(models.TextChoices):
        CREATION = "CREATION", "Credit Created"
        SALE = "SALE", "Sold"
        TRANSFER = "TRANSFER", "Transferred"

    credit = models.ForeignKey(
        "credits.CarbonCredit",
        on_delete=models.CASCADE,
        related_name="ownership_history"
    )
    from_owner = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="credits_transferred_from",
        help_text="Null para criação inicial"
    )
    to_owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="credits_transferred_to"
    )
    transfer_type = models.CharField(
        max_length=16,
        choices=TransferType.choices
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ownership_records"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preço pago na transferência (se aplicável)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Histórico de Propriedade"
        verbose_name_plural = "Históricos de Propriedade"
        indexes = [
            models.Index(fields=['credit', 'timestamp']),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        from_str = self.from_owner.username if self.from_owner else "GENESIS"
        return f"{from_str} → {self.to_owner.username} ({self.transfer_type})"

