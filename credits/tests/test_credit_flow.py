"""Teste e2e do fluxo completo de créditos.

Fluxo: criar crédito → listar → comprar → transferir
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction

User = get_user_model()


class CreditFlowTestCase(TestCase):
    """Teste end-to-end do fluxo completo de transação de créditos."""

    def setUp(self):
        """Configura usuários para o teste e2e."""
        # Criar usuários
        self.producer = User.objects.create_user(
            username="producer1",
            password="testpass123",
            email="producer@test.com",
            role="PRODUCER",
        )
        self.company = User.objects.create_user(
            username="company1",
            password="testpass123",
            email="company@test.com",
            role="COMPANY",
        )
        self.client = Client()

    def test_full_credit_flow(self):
        """Teste e2e do fluxo completo: criar crédito → listar → comprar → transferir."""

        # ===== FASE 1: PRODUTOR CRIA CRÉDITO =====
        self.client.login(username="producer1", password="testpass123")

        credit_data = {
            "amount": "100.00",
            "origin": "Test Farm E2E",
            "generation_date": "2025-10-29",
            "unit": "tCO2e",
        }
        response = self.client.post(reverse("credit_create"), credit_data, follow=True)

        credit = CarbonCredit.objects.first()
        self.assertIsNotNone(credit, "Crédito deve ter sido criado")
        self.assertEqual(credit.owner, self.producer)
        self.assertEqual(credit.amount, Decimal("100.00"))
        self.assertEqual(credit.status, CarbonCredit.Status.AVAILABLE)

        # ===== FASE 2: PRODUTOR LISTA CRÉDITO PARA VENDA =====
        listing_data = {"price_per_unit": "50.00"}
        response = self.client.post(
            reverse("credit_list_for_sale", kwargs={"pk": credit.id}),
            listing_data,
            follow=True,
        )

        listing = CreditListing.objects.first()
        self.assertIsNotNone(listing, "Listing deve ter sido criado")
        self.assertEqual(listing.credit, credit)
        self.assertTrue(listing.is_active)
        self.assertEqual(listing.price_per_unit, Decimal("50.00"))

        # Verificar se o status do crédito mudou para LISTED
        credit.refresh_from_db()
        self.assertEqual(credit.status, CarbonCredit.Status.LISTED)

        # ===== FASE 3: EMPRESA COMPRA CRÉDITO =====
        self.client.logout()
        self.client.login(username="company1", password="testpass123")

        response = self.client.post(
            reverse("credit_buy", kwargs={"pk": credit.id}), follow=True
        )
        self.assertEqual(response.status_code, 200)

        # ===== FASE 4: VERIFICAR TRANSFERÊNCIA COMPLETA =====

        # Verificar transação criada
        transaction = Transaction.objects.first()
        self.assertIsNotNone(transaction, "Transação deve ter sido criada")
        self.assertEqual(transaction.buyer, self.company)
        self.assertEqual(transaction.seller, self.producer)
        self.assertEqual(transaction.status, Transaction.Status.COMPLETED)
        self.assertEqual(transaction.amount, Decimal("100.00"))
        self.assertEqual(transaction.total_price, Decimal("5000.00"))  # 100 * 50

        # Verificar propriedade transferida
        credit.refresh_from_db()
        self.assertEqual(credit.owner, self.company, "Propriedade deve ter sido transferida")
        self.assertEqual(credit.status, CarbonCredit.Status.SOLD)

        # Verificar listing desativado
        listing.refresh_from_db()
        self.assertFalse(listing.is_active, "Listing deve estar desativado")