"""Management command to seed CarbonCredit data."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from accounts.models import User
from credits.models import CarbonCredit
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with CarbonCredit data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=45,
            help='Number of credits to create (default: 45)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        count = options['count']

        # Check for producer users
        producers = User.objects.filter(role=User.Roles.PRODUCER)
        if not producers.exists():
            self.stdout.write(
                self.style.ERROR('No PRODUCER users found. Run seed_users first.')
            )
            return

        # Brazilian regions for carbon credit origin
        regions = [
            'Amazônia, AM', 'Mata Atlântica, SP', 'Cerrado, GO',
            'Pantanal, MS', 'Caatinga, BA', 'Pampa, RS',
            'Vale do Paraíba, SP', 'Região Sul, PR', 'Nordeste, CE',
            'Centro-Oeste, MT', 'Norte, PA', 'Sudeste, MG'
        ]

        created_credits = []

        self.stdout.write(f'Creating {count} CarbonCredit records...')

        for i in range(count):
            owner = random.choice(producers)

            # Generate realistic data
            amount = fake.pydecimal(
                left_digits=4,
                right_digits=2,
                positive=True,
                min_value=10,
                max_value=1000
            )

            # Generation date within last 2 years
            days_ago = random.randint(30, 730)
            generation_date = (timezone.now() - timedelta(days=days_ago)).date()

            # Status distribution: 60% AVAILABLE, 30% LISTED, 10% SOLD
            status_choice = random.choices(
                [CarbonCredit.Status.AVAILABLE, CarbonCredit.Status.LISTED, CarbonCredit.Status.SOLD],
                weights=[60, 30, 10]
            )[0]

            credit = CarbonCredit.objects.create(
                owner=owner,
                amount=amount,
                origin=random.choice(regions),
                generation_date=generation_date,
                status=status_choice,
                unit='tons CO2',
                is_verified=fake.boolean(chance_of_getting_true=80)
            )

            created_credits.append(credit)

        # Summary stats
        total = len(created_credits)
        available = sum(1 for c in created_credits if c.status == CarbonCredit.Status.AVAILABLE)
        listed = sum(1 for c in created_credits if c.status == CarbonCredit.Status.LISTED)
        sold = sum(1 for c in created_credits if c.status == CarbonCredit.Status.SOLD)
        verified = sum(1 for c in created_credits if c.is_verified)

        # Count ownership history entries created by signals
        from credits.models import CreditOwnershipHistory
        history_count = CreditOwnershipHistory.objects.filter(
            credit__in=created_credits,
            transfer_type=CreditOwnershipHistory.TransferType.CREATION
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created {total} credits: '
                f'{available} available, {listed} listed, {sold} sold '
                f'({verified} verified)\n'
                f'✓ Created {history_count} GENESIS ownership records (via signals)'
            )
        )
