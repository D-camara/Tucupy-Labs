from django.test import TestCase
from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class TransactionModelTestCase(TestCase):
    def setUp(self):
        self.producer = User.objects.create_user(
            username='producer1',
            email='producer@test.com',
            password='testpass123',
            role='PRODUCER'
        )
        self.company = User.objects.create_user(
            username='company1',
            email='company@test.com',
            password='testpass123',
            role='COMPANY'
        )
        
        # Criar um crédito
        self.credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal('100.00'),
            origin='Test Farm',
            generation_date='2025-10-29',
            status='AVAILABLE'
        )

    def test_transaction_creation(self):
        """Testa a criação básica de uma transação"""
        transaction = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal('50.00'),
            total_price=Decimal('2500.00'),  # 50 * 50.00
            status='PENDING'
        )
        
        self.assertEqual(transaction.buyer, self.company)
        self.assertEqual(transaction.seller, self.producer)
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.status, 'PENDING')