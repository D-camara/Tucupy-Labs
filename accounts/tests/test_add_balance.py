"""Testes para a view de adicionar saldo."""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class AddBalanceViewTests(TestCase):
    """Testes da view de adicionar saldo."""

    def setUp(self):
        """Configura usuários para testes."""
        self.client = Client()
        
        # Criar empresa
        self.company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )
        
        # Criar produtor
        self.producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )

    def test_add_balance_requires_authentication(self):
        """Adicionar saldo requer autenticação."""
        resp = self.client.get(reverse("accounts:add_balance"))
        # Redireciona para login
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_add_balance_requires_company_role(self):
        """Apenas empresas podem adicionar saldo."""
        self.client.force_login(self.producer)
        resp = self.client.get(reverse("accounts:add_balance"))
        # Pode ser 403 (PermissionDenied) ou 302 (redirect)
        self.assertIn(resp.status_code, [302, 403])

    def test_add_balance_get_shows_form(self):
        """GET exibe formulário com saldo atual."""
        self.client.force_login(self.company)
        resp = self.client.get(reverse("accounts:add_balance"))
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Adicionar Saldo")
        self.assertContains(resp, "Saldo Atual")

    def test_add_balance_success(self):
        """Empresa pode adicionar saldo com sucesso."""
        self.client.force_login(self.company)
        
        # Saldo inicial
        self.assertEqual(self.company.profile.balance, Decimal("0"))
        
        # Adicionar R$ 1000
        resp = self.client.post(
            reverse("accounts:add_balance"),
            {"amount": "1000.00"},
            follow=True
        )
        
        self.assertEqual(resp.status_code, 200)
        
        # Verificar que o saldo foi atualizado
        self.company.profile.refresh_from_db()
        self.assertEqual(self.company.profile.balance, Decimal("1000.00"))
        
        # Verificar mensagem de sucesso
        messages = list(resp.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("✅", str(messages[0]))

    def test_add_balance_invalid_amount(self):
        """Não pode adicionar valor inválido."""
        self.client.force_login(self.company)
        
        # Tentar adicionar valor negativo
        resp = self.client.post(
            reverse("accounts:add_balance"),
            {"amount": "-100"},
            follow=True
        )
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "maior que zero")
        
        # Saldo não deve ter mudado
        self.company.profile.refresh_from_db()
        self.assertEqual(self.company.profile.balance, Decimal("0"))

    def test_add_balance_empty_amount(self):
        """Não pode adicionar sem informar valor."""
        self.client.force_login(self.company)
        
        resp = self.client.post(
            reverse("accounts:add_balance"),
            {"amount": ""},
            follow=True
        )
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "informe o valor")

    def test_add_balance_too_high(self):
        """Não pode adicionar valor muito alto."""
        self.client.force_login(self.company)
        
        resp = self.client.post(
            reverse("accounts:add_balance"),
            {"amount": "2000000"},  # > 1.000.000
            follow=True
        )
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "muito alto")
