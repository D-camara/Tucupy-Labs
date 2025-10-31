"""
Management command para adicionar saldo a um usuário.
Uso: python manage.py add_balance <username> <amount>
"""
from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Adiciona saldo à carteira de um usuário'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome do usuário')
        parser.add_argument('amount', type=float, help='Valor a adicionar (R$)')

    def handle(self, *args, **options):
        username = options['username']
        amount = Decimal(str(options['amount']))
        
        if amount <= 0:
            raise CommandError('O valor deve ser maior que zero')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Usuário "{username}" não encontrado')
        
        old_balance = user.profile.balance
        user.profile.add_balance(amount)
        new_balance = user.profile.balance
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Saldo adicionado com sucesso!\n'
                f'Usuário: {username}\n'
                f'Saldo anterior: R$ {old_balance:.2f}\n'
                f'Valor adicionado: R$ {amount:.2f}\n'
                f'Novo saldo: R$ {new_balance:.2f}'
            )
        )
