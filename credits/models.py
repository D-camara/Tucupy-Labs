from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
    is_verified = models.BooleanField(default=False, help_text="Crédito verificado por administrador")

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

