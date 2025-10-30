"""Testes dos models de transações."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from credits.models import CarbonCredit
from transactions.models import Transaction

User = get_user_model()


class TransactionModelTestCase(TestCase):
    """Testes do model Transaction."""

    def setUp(self):
        """Configura usuários e crédito para testes."""
        self.producer = User.objects.create_user(
            username="producer1",
            email="producer@test.com",
            password="testpass123",
            role="PRODUCER",
        )
        self.company = User.objects.create_user(
            username="company1",
            email="company@test.com",
            password="testpass123",
            role="COMPANY",
        )

        # Criar um crédito
        self.credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("100.00"),
            origin="Test Farm",
            generation_date="2025-10-29",
            status="AVAILABLE",
        )

    def test_transaction_creation(self):
        """Testa a criação básica de uma transação."""
        transaction = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal("50.00"),
            total_price=Decimal("2500.00"),  # 50 * 50.00
            status="PENDING",
        )

        self.assertEqual(transaction.buyer, self.company)
        self.assertEqual(transaction.seller, self.producer)
        self.assertEqual(transaction.amount, Decimal("50.00"))
        self.assertEqual(transaction.status, "PENDING")

    def test_transaction_default_status(self):
        """Testa que o status padrão é PENDING."""
        transaction = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal("100.00"),
            total_price=Decimal("5000.00"),
        )

        self.assertEqual(transaction.status, Transaction.Status.PENDING)

    def test_transaction_str_representation(self):
        """Testa a representação em string da transação."""
        transaction = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal("100.00"),
            total_price=Decimal("5000.00"),
            status="COMPLETED",
        )

        str_repr = str(transaction)
        self.assertIn(f"Txn#{transaction.id}", str_repr)
        self.assertIn("company1", str_repr)
        self.assertIn("producer1", str_repr)
        self.assertIn("COMPLETED", str_repr)