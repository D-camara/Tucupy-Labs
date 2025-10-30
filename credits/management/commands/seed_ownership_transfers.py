"""Management command to seed complex ownership transfer chains (blockchain demo)."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction
from faker import Faker
from accounts.models import User
from credits.models import CarbonCredit, CreditOwnershipHistory
from transactions.models import Transaction
from datetime import timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed complex ownership transfer chains for blockchain-style history demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--chains',
            type=int,
            default=5,
            help='Number of transfer chains to create (default: 5)'
        )
        parser.add_argument(
            '--depth',
            type=int,
            default=4,
            help='Number of transfers per chain (default: 4)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        chains = options['chains']
        depth = options['depth']

        # Check for required users
        producers = list(User.objects.filter(role=User.Roles.PRODUCER))
        companies = list(User.objects.filter(role=User.Roles.COMPANY))

        if len(producers) < 1:
            self.stdout.write(
                self.style.ERROR('Need at least 1 PRODUCER. Run seed_users first.')
            )
            return

        if len(companies) < depth:
            self.stdout.write(
                self.style.ERROR(f'Need at least {depth} COMPANY users. Run seed_users first.')
            )
            return

        created_credits = []
        created_transactions = []
        total_transfers = 0

        self.stdout.write(f'Creating {chains} transfer chains with {depth} transfers each...')

        regions = [
            'Amazônia, AM', 'Mata Atlântica, SP', 'Cerrado, GO',
            'Pantanal, MS', 'Caatinga, BA', 'Pampa, RS',
        ]

        for chain_num in range(chains):
            with db_transaction.atomic():
                # 1. Create initial credit (producer is first owner)
                producer = random.choice(producers)

                amount = fake.pydecimal(
                    left_digits=3,
                    right_digits=2,
                    positive=True,
                    min_value=50,
                    max_value=500
                )

                # Start date 1-2 years ago
                start_days_ago = random.randint(365, 730)
                generation_date = (timezone.now() - timedelta(days=start_days_ago)).date()

                credit = CarbonCredit.objects.create(
                    owner=producer,
                    amount=amount,
                    origin=random.choice(regions),
                    generation_date=generation_date,
                    status=CarbonCredit.Status.AVAILABLE,
                    unit='tons CO2',
                    is_verified=True  # All demo credits are verified
                )
                created_credits.append(credit)

                self.stdout.write(
                    f'  Chain #{chain_num + 1}: Credit #{credit.id} created by {producer.username}'
                )

                # 2. Create transfer chain (each company buys from previous owner)
                current_owner = producer
                days_elapsed = start_days_ago

                # Randomly select unique companies for this chain
                chain_buyers = random.sample(companies, min(depth, len(companies)))

                for transfer_num, buyer in enumerate(chain_buyers):
                    # Calculate price (increases 5-15% with each transfer)
                    base_price = Decimal('80.00') if transfer_num == 0 else last_price
                    price_increase = Decimal(str(random.uniform(1.05, 1.15)))
                    price_per_unit = (base_price * price_increase).quantize(Decimal('0.01'))
                    last_price = price_per_unit

                    total_price = (amount * price_per_unit).quantize(Decimal('0.01'))

                    # Time between transfers: 30-180 days
                    days_between = random.randint(30, 180)
                    days_elapsed -= days_between
                    transfer_time = timezone.now() - timedelta(days=days_elapsed)

                    # Create completed transaction
                    txn = Transaction.objects.create(
                        buyer=buyer,
                        seller=current_owner,
                        credit=credit,
                        amount=amount,
                        total_price=total_price,
                        status=Transaction.Status.COMPLETED
                    )
                    txn.timestamp = transfer_time
                    txn.save()
                    created_transactions.append(txn)

                    # Transfer ownership (signal creates history entry)
                    credit.owner = buyer
                    credit.status = CarbonCredit.Status.SOLD
                    credit.save()

                    self.stdout.write(
                        f'    Transfer #{transfer_num + 1}: '
                        f'{current_owner.username} → {buyer.username} '
                        f'(R$ {total_price:.2f}) '
                        f'[{transfer_time.strftime("%Y-%m-%d")}]'
                    )

                    current_owner = buyer
                    total_transfers += 1

        # Summary stats
        self.stdout.write('\n' + '='*60)

        # Count history entries
        history_entries = CreditOwnershipHistory.objects.filter(
            credit__in=created_credits
        ).count()

        creation_entries = CreditOwnershipHistory.objects.filter(
            credit__in=created_credits,
            transfer_type=CreditOwnershipHistory.TransferType.CREATION
        ).count()

        sale_entries = CreditOwnershipHistory.objects.filter(
            credit__in=created_credits,
            transfer_type=CreditOwnershipHistory.TransferType.SALE
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Created {len(created_credits)} credits with transfer chains\n'
                f'✓ Created {len(created_transactions)} completed transactions\n'
                f'✓ Total ownership transfers: {total_transfers}\n'
                f'✓ History entries created: {history_entries} '
                f'({creation_entries} GENESIS + {sale_entries} SALE)\n\n'
                f'💡 Tip: View history at /credits/<id>/history/'
            )
        )

        # Show example URLs
        if created_credits:
            self.stdout.write('\nExample history URLs:')
            for credit in created_credits[:3]:
                transfer_count = credit.ownership_history.count() - 1  # -1 for GENESIS
                self.stdout.write(
                    f'  • Credit #{credit.id}: /credits/{credit.id}/history/ '
                    f'({transfer_count} transfers)'
                )
