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
class CarbonCreditUnit(models.Model):                                            #modelo de cada unidade de Carbono
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey("accounts.Project", on_delete=models.PROTECT, related_name="project") #projeto associado ao credito
    current_owner = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="user") #dono atual desse credito de Carbono
    status = models.ForeignKey("Transactions.Status", on_delete=models.PROTECT, related_name="status")

class UserPortfolio(models.Model):                                               #saldo de creditos de Carbono de cada usuario/empresa
    id = models.BigAutoField(primary_key=True)          
    total_units_holding = models.DecimalField(max_digits=12, decimal_places=2)   #total de creditos possuidos, precisa ser calculado dinamicamente 
    is_locked = models.BooleanField()                                            #booleana para garantir segurança

class Transaction(models.Model):                #modelo das transacoes
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"    #disponivel p/ compra
        LOCKED = "LOCKED", "Locked"             #trancado para transacao, nao disponivel ate que seja finalizado
        RETIRED = "RETIRED", "Retired"          #nao mais disponivel p/ compra, apagar do banco imediatamente

    transaction_id = models.BigAutoField(primary_key=True)
    seller_fk = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name='user') #'quem esta vendendo'
    buyer_fk = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name='user')  #'quem esta comprando'
    timestamp = models.DateField(auto_now=True)                                                   #hora e data da transacao
    unit_id = models.ForeignKey("CarbonCreditUnit", on_delete=models.PROTECT, related_name='unit')#identificador do credito sendo comprado



