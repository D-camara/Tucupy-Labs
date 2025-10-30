"""Management command to display ownership history statistics."""
from django.core.management.base import BaseCommand
from credits.models import CarbonCredit, CreditOwnershipHistory
from django.db.models import Count


class Command(BaseCommand):
    help = 'Display ownership history statistics across all credits'

    def handle(self, *args, **options):
        # Total counts
        total_credits = CarbonCredit.objects.count()
        total_history = CreditOwnershipHistory.objects.count()

        # By transfer type
        creation_count = CreditOwnershipHistory.objects.filter(
            transfer_type=CreditOwnershipHistory.TransferType.CREATION
        ).count()
        sale_count = CreditOwnershipHistory.objects.filter(
            transfer_type=CreditOwnershipHistory.TransferType.SALE
        ).count()
        transfer_count = CreditOwnershipHistory.objects.filter(
            transfer_type=CreditOwnershipHistory.TransferType.TRANSFER
        ).count()

        # Credits with multiple owners
        credits_with_transfers = CarbonCredit.objects.annotate(
            history_count=Count('ownership_history')
        ).filter(history_count__gt=1)

        multi_owner_count = credits_with_transfers.count()

        # Most transferred credit
        most_transferred = CarbonCredit.objects.annotate(
            transfer_count=Count('ownership_history')
        ).order_by('-transfer_count').first()

        # Display stats
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('  OWNERSHIP HISTORY STATISTICS'))
        self.stdout.write('='*60 + '\n')

        self.stdout.write(f'Total Credits:           {total_credits}')
        self.stdout.write(f'Total History Entries:   {total_history}\n')

        self.stdout.write('Breakdown by Type:')
        self.stdout.write(f'  • CREATION (Genesis):  {creation_count}')
        self.stdout.write(f'  • SALE (Marketplace):  {sale_count}')
        self.stdout.write(f'  • TRANSFER (Manual):   {transfer_count}\n')

        self.stdout.write(f'Credits with transfers:  {multi_owner_count}\n')

        if most_transferred:
            transfer_count = most_transferred.ownership_history.count()
            unique_owners = transfer_count  # Each history entry has a to_owner
            self.stdout.write('Most Transferred Credit:')
            self.stdout.write(f'  • Credit #{most_transferred.id}')
            self.stdout.write(f'  • Total owners: {unique_owners}')
            self.stdout.write(f'  • Current owner: {most_transferred.owner.username}')
            self.stdout.write(f'  • View: /credits/{most_transferred.id}/history/\n')

        # Recent transfers
        recent_sales = CreditOwnershipHistory.objects.filter(
            transfer_type=CreditOwnershipHistory.TransferType.SALE
        ).select_related('credit', 'from_owner', 'to_owner').order_by('-timestamp')[:5]

        if recent_sales:
            self.stdout.write('Recent Sales:')
            for sale in recent_sales:
                from_name = sale.from_owner.username if sale.from_owner else 'GENESIS'
                self.stdout.write(
                    f'  • Credit #{sale.credit_id}: '
                    f'{from_name} → {sale.to_owner.username} '
                    f'({sale.timestamp.strftime("%Y-%m-%d %H:%M")})'
                )

        self.stdout.write('\n' + '='*60)
