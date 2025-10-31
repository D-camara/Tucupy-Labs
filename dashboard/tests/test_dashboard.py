"""Testes do Dashboard.

Este arquivo verifica:
- Dashboard requer autenticação
- Métricas corretas por papel (Producer/Company)
- Visualização de transações recentes
- Contadores de créditos e vendas
"""

from __future__ import annotations

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction
from decimal import Decimal


class DashboardViewTests(TestCase):
    """Testes da view principal do dashboard."""

    def setUp(self):
        """Configura usuários e dados de teste."""
        self.client = Client()
        
        # Criar produtor
        self.producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )
        
        # Criar empresa
        self.company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )
        
        # Criar créditos do produtor
        self.credit1 = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("100.00"),
            origin="Farm A",
            generation_date="2025-10-01",
            status="AVAILABLE",
        )
        
        self.credit2 = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("50.00"),
            origin="Farm B",
            generation_date="2025-10-15",
            status="AVAILABLE",
        )

    def test_dashboard_requires_login(self):
        """Dashboard redireciona usuários não autenticados."""
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_dashboard_loads_for_authenticated_user(self):
        """Dashboard carrega para usuário autenticado."""
        self.client.force_login(self.producer)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dashboard")

    def test_producer_sees_correct_metrics(self):
        """Produtor vê métricas corretas: carteira, créditos listados, total de vendas."""
        self.client.force_login(self.producer)
        
        # Criar listing para um crédito
        CreditListing.objects.create(
            credit=self.credit1,
            price_per_unit=Decimal("50.00"),
            is_active=True,
        )
        
        # Criar transação completada
        Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit2,
            amount=Decimal("50.00"),
            total_price=Decimal("2500.00"),
            status="COMPLETED",
        )
        
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        
        # Verifica contexto
        self.assertEqual(resp.context["my_credits"], Decimal("150.00"))  # 100 + 50
        self.assertEqual(resp.context["listed_credits"], 1)
        self.assertEqual(resp.context["total_sales"], Decimal("2500.00"))

    def test_company_sees_correct_metrics(self):
        """Empresa vê métricas corretas: créditos disponíveis, total adquirido."""
        self.client.force_login(self.company)
        
        # Criar listings ativos
        CreditListing.objects.create(
            credit=self.credit1,
            price_per_unit=Decimal("50.00"),
            is_active=True,
        )
        
        CreditListing.objects.create(
            credit=self.credit2,
            price_per_unit=Decimal("40.00"),
            is_active=True,
        )
        
        # Criar transação completada
        Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit1,
            amount=Decimal("100.00"),
            total_price=Decimal("5000.00"),
            status="COMPLETED",
        )
        
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        
        # Verifica contexto
        self.assertEqual(resp.context["available_credits"], 2)
        self.assertEqual(resp.context["total_purchased"], Decimal("100.00"))

    def test_dashboard_shows_recent_transactions(self):
        """Dashboard exibe últimas 5 transações do usuário."""
        self.client.force_login(self.company)
        
        # Criar 6 transações
        for i in range(6):
            Transaction.objects.create(
                buyer=self.company,
                seller=self.producer,
                credit=self.credit1,
                amount=Decimal("10.00"),
                total_price=Decimal("500.00"),
                status="PENDING",
            )
        
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        
        # Deve mostrar apenas 5 transações
        self.assertEqual(len(resp.context["recent_transactions"]), 5)


class AdminRegistrationTests(TestCase):
    """Testes para verificar se models estão registrados no admin."""

    def test_user_model_registered_in_admin(self):
        """Model User está registrado no admin."""
        from django.contrib import admin
        from accounts.models import User
        
        self.assertTrue(admin.site.is_registered(User))

    def test_profile_model_registered_in_admin(self):
        """Model Profile está registrado no admin."""
        from django.contrib import admin
        from accounts.models import Profile
        
        self.assertTrue(admin.site.is_registered(Profile))

    def test_credit_model_registered_in_admin(self):
        """Model CarbonCredit está registrado no admin."""
        from django.contrib import admin
        from credits.models import CarbonCredit
        
        self.assertTrue(admin.site.is_registered(CarbonCredit))

    def test_listing_model_registered_in_admin(self):
        """Model CreditListing está registrado no admin."""
        from django.contrib import admin
        from credits.models import CreditListing
        
        self.assertTrue(admin.site.is_registered(CreditListing))

    def test_transaction_model_registered_in_admin(self):
        """Model Transaction está registrado no admin."""
        from django.contrib import admin
        from transactions.models import Transaction
        
        self.assertTrue(admin.site.is_registered(Transaction))
