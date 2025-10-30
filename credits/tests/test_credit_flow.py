"""Teste e2e do fluxo completo de créditos.

Este teste será implementado após a Task 4 (Transações) estar completa.
Fluxo: criar crédito → listar → comprar → transferir
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction
from decimal import Decimal

User = get_user_model()


class CreditFlowTestCase(TestCase):
    """Testes do fluxo e2e de créditos (parcial - aguarda Task 4)."""

    def setUp(self):
        """Configura usuários de teste."""
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

    def test_create_and_list_credit_flow(self):
        """Teste e2e parcial: criar crédito → listar no marketplace."""
        # Login como produtor
        self.client.login(username="producer1", password="testpass123")

        # 1. Criar crédito (incluir unit que é obrigatório)
        credit_data = {
            "amount": "100.00",
            "origin": "Test Farm",
            "generation_date": "2025-10-29",
            "unit": "tCO2e",  # Campo obrigatório
        }
        response = self.client.post(reverse("credit_create"), credit_data, follow=True)
        
        # Verifica se o crédito foi criado
        credit = CarbonCredit.objects.first()
        self.assertIsNotNone(credit, "Crédito deveria ter sido criado")
        self.assertEqual(credit.owner, self.producer)
        self.assertEqual(credit.amount, Decimal("100.00"))
        self.assertEqual(credit.status, "AVAILABLE")

        # 2. Listar crédito para venda
        response = self.client.post(
            reverse("credit_list_for_sale", kwargs={"pk": credit.id}),
            {"price_per_unit": Decimal("50.00")},
        )
        self.assertEqual(response.status_code, 302)

        listing = CreditListing.objects.first()
        self.assertIsNotNone(listing)
        self.assertEqual(listing.credit, credit)
        self.assertTrue(listing.is_active)

        # Verificar se o status do crédito mudou para LISTED
        credit.refresh_from_db()
        self.assertEqual(credit.status, "LISTED")

        # 3. Verificar que o crédito aparece no marketplace
        self.client.logout()
        self.client.login(username="company1", password="testpass123")

        response = self.client.get(reverse("credits_marketplace"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Farm")
        self.assertContains(response, "100.00")

    # TODO: Implementar após Task 4 (Transações)
    # def test_full_credit_flow_with_purchase(self):
    #     """Teste e2e completo: criar → listar → comprar → transferir"""
    #     pass