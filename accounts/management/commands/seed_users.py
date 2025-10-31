"""Management command to seed User and Profile data."""
from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User, Profile


class Command(BaseCommand):
    help = 'Seed database with User and Profile data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=35,
            help='Number of users to create (default: 35)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        count = options['count']

        # Distribution: ~60% companies, ~35% producers, ~5% admins
        company_count = int(count * 0.6)
        producer_count = int(count * 0.35)
        admin_count = max(1, count - company_count - producer_count)

        created_users = []

        # Create companies
        self.stdout.write(f'Creating {company_count} COMPANY users...')
        for i in range(company_count):
            username = f"company_{fake.user_name()}_{i}"
            user = User.objects.create_user(
                username=username,
                email=fake.company_email(),
                password='password123',
                role=User.Roles.COMPANY,
                is_verified=fake.boolean(chance_of_getting_true=85)
            )

            # Update profile with company data
            profile = user.profile
            profile.company_name = fake.company()
            profile.location = f"{fake.city()}, {fake.state_abbr()}"
            profile.tax_id = fake.cnpj()
            profile.phone = fake.phone_number()
            profile.balance = fake.pydecimal(left_digits=5, right_digits=2, positive=True, min_value=1000, max_value=50000)
            profile.save()

            created_users.append(user)

        # Create producers
        self.stdout.write(f'Creating {producer_count} PRODUCER users...')
        for i in range(producer_count):
            username = f"producer_{fake.user_name()}_{i}"
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                role=User.Roles.PRODUCER,
                is_verified=fake.boolean(chance_of_getting_true=90)
            )

            # Update profile with farm data
            profile = user.profile
            profile.farm_name = f"Fazenda {fake.last_name()}"
            profile.location = f"{fake.city()}, {fake.state_abbr()}"
            profile.tax_id = fake.cpf()
            profile.phone = fake.phone_number()
            profile.balance = 0  # Producers don't need balance
            profile.save()

            created_users.append(user)

        # Create admins
        self.stdout.write(f'Creating {admin_count} ADMIN users...')
        for i in range(admin_count):
            username = f"admin_{fake.user_name()}_{i}"
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                role=User.Roles.ADMIN,
                is_staff=True,
                is_superuser=True,
                is_verified=True
            )

            created_users.append(user)

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created {len(created_users)} users '
                f'({company_count} companies, {producer_count} producers, {admin_count} admins)'
            )
        )
