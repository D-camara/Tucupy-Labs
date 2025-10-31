"""Signals para rastreamento automático de propriedade de créditos."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CarbonCredit, CreditOwnershipHistory


@receiver(post_save, sender=CarbonCredit)
def track_credit_ownership(sender, instance, created, **kwargs):
    """
    Cria registro de histórico de propriedade automaticamente.

    - Na criação: primeiro registro com from_owner=None (GENESIS)
    - Na mudança de owner: novo registro com transfer_type=SALE ou TRANSFER
    """
    if created:
        # Primeira entrada: criação do crédito
        CreditOwnershipHistory.objects.create(
            credit=instance,
            from_owner=None,  # GENESIS
            to_owner=instance.owner,
            transfer_type=CreditOwnershipHistory.TransferType.CREATION,
            notes=f"Crédito criado: {instance.amount} {instance.unit} de {instance.origin}"
        )
    else:
        # Verificar se houve mudança de propriedade
        # Buscar o owner anterior do último registro
        last_history = instance.ownership_history.last()

        # Handle legacy credits without history (create GENESIS entry)
        if not last_history:
            CreditOwnershipHistory.objects.create(
                credit=instance,
                from_owner=None,
                to_owner=instance.owner,
                transfer_type=CreditOwnershipHistory.TransferType.CREATION,
                notes="Entrada retroativa para crédito legado"
            )
        elif last_history.to_owner != instance.owner:
            # Owner mudou - criar novo registro
            # Inferir tipo de transferência baseado no status
            transfer_type = (
                CreditOwnershipHistory.TransferType.SALE
                if instance.status == CarbonCredit.Status.SOLD
                else CreditOwnershipHistory.TransferType.TRANSFER
            )

            # Buscar transação relacionada se existir
            related_transaction = None
            if transfer_type == CreditOwnershipHistory.TransferType.SALE:
                # Pegar a transação mais recente COMPLETED para este crédito
                related_transaction = instance.transactions.filter(
                    status='COMPLETED',
                    buyer=instance.owner
                ).order_by('-timestamp').first()

            CreditOwnershipHistory.objects.create(
                credit=instance,
                from_owner=last_history.to_owner,
                to_owner=instance.owner,
                transfer_type=transfer_type,
                transaction=related_transaction,
                price=related_transaction.total_price if related_transaction else None,
            )
