from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction
from decimal import Decimal

User = get_user_model()

class CreditFlowTestCase(TestCase):
    def setUp(self):
        # Criar usuários
        self.producer = User.objects.create_user(
            username='producer1',
            password='testpass123',
            email='producer@test.com',
            role='PRODUCER'
        )
        self.company = User.objects.create_user(
            username='company1',
            password='testpass123',
            email='company@test.com',
            role='COMPANY'
        )
        self.client = Client()

    def test_full_credit_flow(self):
        """Teste e2e do fluxo completo: criar crédito → listar → comprar → transferir"""
        
        # Login como produtor
        self.client.login(username='producer1', password='testpass123')
        
        # 1. Criar crédito
        credit_data = {
            'amount': Decimal('100.00'),
            'origin': 'Test Farm',
            'generation_date': '2025-10-29'
        }
        response = self.client.post(reverse('credits:create'), credit_data)
        self.assertEqual(response.status_code, 302)  # Redirecionamento após sucesso
        
        credit = CarbonCredit.objects.first()
        self.assertIsNotNone(credit)
        self.assertEqual(credit.owner, self.producer)
        self.assertEqual(credit.amount, Decimal('100.00'))
        
        # 2. Criar listing
        listing_data = {
            'credit': credit.id,
            'price_per_unit': Decimal('50.00')
        }
        response = self.client.post(reverse('credits:list'), listing_data)
        self.assertEqual(response.status_code, 302)
        
        listing = CreditListing.objects.first()
        self.assertIsNotNone(listing)
        self.assertEqual(listing.credit, credit)
        self.assertTrue(listing.is_active)
        
        # Verificar se o status do crédito mudou para LISTED
        credit.refresh_from_db()
        self.assertEqual(credit.status, 'LISTED')
        
        # Login como empresa
        self.client.logout()
        self.client.login(username='company1', password='testpass123')
        
        # 3. Comprar crédito
        buy_data = {
            'listing_id': listing.id,
            'amount': Decimal('100.00')  # Compra total
        }
        response = self.client.post(
            reverse('credits:buy', kwargs={'pk': credit.id}),
            buy_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar a transação e transferência
        transaction = Transaction.objects.first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.buyer, self.company)
        self.assertEqual(transaction.seller, self.producer)
        self.assertEqual(transaction.status, 'COMPLETED')
        
        # Verificar se a propriedade foi transferida
        credit.refresh_from_db()
        self.assertEqual(credit.owner, self.company)
        self.assertEqual(credit.status, 'SOLD')
        
        # Verificar se o listing foi desativado
        listing.refresh_from_db()
        self.assertFalse(listing.is_active)