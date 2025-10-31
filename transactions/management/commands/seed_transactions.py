"""Management command to seed Transaction data."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from accounts.models import User
from credits.models import CarbonCredit
from transactions.models import Transaction
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with Transaction data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=35,
            help='Number of transactions to create (default: 35)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        count = options['count']

        # Check for required data
        companies = User.objects.filter(role=User.Roles.COMPANY)
        producers = User.objects.filter(role=User.Roles.PRODUCER)
        credits = CarbonCredit.objects.all()

        if not companies.exists():
            self.stdout.write(
                self.style.ERROR('No COMPANY users found. Run seed_users first.')
            )
            return

        if not producers.exists():
            self.stdout.write(
                self.style.ERROR('No PRODUCER users found. Run seed_users first.')
            )
            return

        if not credits.exists():
            self.stdout.write(
                self.style.ERROR('No CarbonCredit records found. Run seed_credits first.')
            )
            return

        created_transactions = []

        self.stdout.write(f'Creating {count} Transaction records...')

        for i in range(count):
            buyer = random.choice(companies)
            credit = random.choice(credits)
            seller = credit.owner

            # Ensure seller is different from buyer
            if seller == buyer:
                continue

            # Transaction amount matches credit amount
            amount = credit.amount

            # Price per unit: R$50-200
            price_per_unit = fake.pydecimal(
                left_digits=3,
                right_digits=2,
                positive=True,
                min_value=50,
                max_value=200
            )

            total_price = amount * price_per_unit

            # Status distribution: 40% PENDING, 50% COMPLETED, 10% CANCELLED
            status_choice = random.choices(
                [Transaction.Status.PENDING, Transaction.Status.COMPLETED, Transaction.Status.CANCELLED],
                weights=[40, 50, 10]
            )[0]

            # Create transaction (timestamp set by auto_now_add)
            transaction = Transaction.objects.create(
                buyer=buyer,
                seller=seller,
                credit=credit,
                amount=amount,
                total_price=total_price,
                status=status_choice
            )

            # Update timestamp to random date in past 6 months
            days_ago = random.randint(1, 180)
            transaction.timestamp = timezone.now() - timedelta(days=days_ago)
            transaction.save()

            # If completed, transfer ownership and update status
            # NOTE: Ownership history is automatically tracked via Django signals
            # When credit.save() is called with new owner, a SALE history entry is created
            if status_choice == Transaction.Status.COMPLETED:
                credit.owner = buyer
                credit.status = CarbonCredit.Status.SOLD
                credit.save()  # Signal creates ownership history with transaction link

            created_transactions.append(transaction)

        # Summary stats
        total = len(created_transactions)
        pending = sum(1 for t in created_transactions if t.status == Transaction.Status.PENDING)
        completed = sum(1 for t in created_transactions if t.status == Transaction.Status.COMPLETED)
        cancelled = sum(1 for t in created_transactions if t.status == Transaction.Status.CANCELLED)

        # Count ownership history entries created via signals
        from credits.models import CreditOwnershipHistory
        completed_txn_ids = [t.id for t in created_transactions if t.status == Transaction.Status.COMPLETED]
        sale_history_count = CreditOwnershipHistory.objects.filter(
            transaction_id__in=completed_txn_ids,
            transfer_type=CreditOwnershipHistory.TransferType.SALE
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created {total} transactions: '
                f'{pending} pending, {completed} completed, {cancelled} cancelled\n'
                f'✓ Created {sale_history_count} SALE ownership records (via signals)'
            )
        )
