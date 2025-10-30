"""Management command to seed CreditListing data."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from credits.models import CarbonCredit, CreditListing
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with CreditListing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of listings to create (default: 30)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        count = options['count']

        # Get credits that can be listed (AVAILABLE or already LISTED)
        listable_credits = CarbonCredit.objects.filter(
            status__in=[CarbonCredit.Status.AVAILABLE, CarbonCredit.Status.LISTED]
        )

        if not listable_credits.exists():
            self.stdout.write(
                self.style.ERROR('No listable credits found. Run seed_credits first.')
            )
            return

        # Limit count to available credits
        actual_count = min(count, listable_credits.count())

        if actual_count < count:
            self.stdout.write(
                self.style.WARNING(
                    f'Only {actual_count} listable credits available. Creating {actual_count} listings.'
                )
            )

        # Randomly select credits to list
        credits_to_list = random.sample(list(listable_credits), actual_count)

        created_listings = []

        self.stdout.write(f'Creating {actual_count} CreditListing records...')

        for credit in credits_to_list:
            # Price per unit: R$50-200 per ton
            price_per_unit = fake.pydecimal(
                left_digits=3,
                right_digits=2,
                positive=True,
                min_value=50,
                max_value=200
            )

            # Expiration date: 30-180 days in future (or None)
            if fake.boolean(chance_of_getting_true=80):
                days_ahead = random.randint(30, 180)
                expires_at = timezone.now() + timedelta(days=days_ahead)
            else:
                expires_at = None

            # Active status: 90% active
            is_active = fake.boolean(chance_of_getting_true=90)

            listing = CreditListing.objects.create(
                credit=credit,
                price_per_unit=price_per_unit,
                expires_at=expires_at,
                is_active=is_active
            )

            # Update credit status to LISTED
            if credit.status == CarbonCredit.Status.AVAILABLE:
                credit.status = CarbonCredit.Status.LISTED
                credit.save()

            created_listings.append(listing)

        # Summary stats
        total = len(created_listings)
        active = sum(1 for l in created_listings if l.is_active)
        with_expiry = sum(1 for l in created_listings if l.expires_at is not None)

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created {total} listings: '
                f'{active} active, {with_expiry} with expiration date'
            )
        )
