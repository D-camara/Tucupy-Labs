"""Testes das views de transações."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction

User = get_user_model()


class BuyCreditViewTests(TestCase):
    """Testes da view de compra de créditos."""

    def setUp(self):
        """Configura usuários, crédito e listing para testes."""
        self.client = Client()

        # Criar produtor
        self.producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )

        # Criar empresa
        self.company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )
        # Adicionar saldo suficiente para comprar
        self.company.profile.add_balance(Decimal("10000.00"))

        # Criar crédito
        self.credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("100.00"),
            origin="Test Farm",
            generation_date="2025-10-29",
            status=CarbonCredit.Status.AVAILABLE,
        )

        # Criar listing
        self.listing = CreditListing.objects.create(
            credit=self.credit, price_per_unit=Decimal("50.00"), is_active=True
        )

        # Atualizar status do crédito para LISTED
        self.credit.status = CarbonCredit.Status.LISTED
        self.credit.save()

    def test_buy_credit_requires_authentication(self):
        """Compra requer autenticação."""
        resp = self.client.post(reverse("credit_buy", kwargs={"pk": self.credit.id}))
        # Deve retornar 403 ou redirecionar para login
        self.assertIn(resp.status_code, [302, 403])

    def test_buy_credit_requires_company_role(self):
        """Apenas empresas podem comprar créditos."""
        self.client.force_login(self.producer)
        resp = self.client.post(reverse("credit_buy", kwargs={"pk": self.credit.id}))
        # Pode ser 403 (PermissionDenied) ou 302 (redirect)
        self.assertIn(resp.status_code, [302, 403])

    def test_buy_credit_success(self):
        """Empresa pode comprar crédito listado com sucesso."""
        self.client.force_login(self.company)
        resp = self.client.post(
            reverse("credit_buy", kwargs={"pk": self.credit.id}), follow=True
        )

        self.assertEqual(resp.status_code, 200)

        # Verificar que a transação foi criada
        txn = Transaction.objects.first()
        self.assertIsNotNone(txn)
        self.assertEqual(txn.buyer, self.company)
        self.assertEqual(txn.seller, self.producer)
        self.assertEqual(txn.status, Transaction.Status.COMPLETED)
        self.assertEqual(txn.total_price, Decimal("5000.00"))  # 100 * 50

        # Verificar que a propriedade foi transferida
        self.credit.refresh_from_db()
        self.assertEqual(self.credit.owner, self.company)
        self.assertEqual(self.credit.status, CarbonCredit.Status.SOLD)

        # Verificar que o listing foi desativado
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_active)

    def test_buy_credit_not_listed(self):
        """Não pode comprar crédito que não está LISTED."""
        self.credit.status = CarbonCredit.Status.AVAILABLE
        self.credit.save()

        self.client.force_login(self.company)
        resp = self.client.post(
            reverse("credit_buy", kwargs={"pk": self.credit.id}), follow=True
        )

        self.assertEqual(resp.status_code, 200)
        # Não deve ter criado transação
        self.assertEqual(Transaction.objects.count(), 0)

    def test_buy_credit_owner_cannot_buy_own(self):
        """Dono não pode comprar seu próprio crédito."""
        self.client.force_login(self.producer)

        # Tornar o produtor uma empresa temporariamente para testar
        self.producer.role = User.Roles.COMPANY
        self.producer.save()

        resp = self.client.post(
            reverse("credit_buy", kwargs={"pk": self.credit.id}), follow=True
        )

        self.assertEqual(resp.status_code, 200)
        # Não deve ter criado transação
        self.assertEqual(Transaction.objects.count(), 0)

    def test_buy_credit_requires_post(self):
        """Compra requer método POST."""
        self.client.force_login(self.company)
        resp = self.client.get(reverse("credit_buy", kwargs={"pk": self.credit.id}))
        self.assertEqual(resp.status_code, 405)  # Method Not Allowed


class TransactionHistoryViewTests(TestCase):
    """Testes da view de histórico de transações."""

    def setUp(self):
        """Configura usuários e transações para testes."""
        self.client = Client()

        # Criar usuários
        self.producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )
        self.company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )

        # Criar crédito
        self.credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("100.00"),
            origin="Test Farm",
            generation_date="2025-10-29",
            status=CarbonCredit.Status.AVAILABLE,
        )

        # Criar transações
        self.txn1 = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal("100.00"),
            total_price=Decimal("5000.00"),
            status=Transaction.Status.COMPLETED,
        )

        self.txn2 = Transaction.objects.create(
            buyer=self.company,
            seller=self.producer,
            credit=self.credit,
            amount=Decimal("50.00"),
            total_price=Decimal("2500.00"),
            status=Transaction.Status.PENDING,
        )

    def test_history_requires_authentication(self):
        """Histórico requer autenticação."""
        resp = self.client.get(reverse("transaction_history"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_history_shows_user_transactions(self):
        """Histórico mostra transações do usuário."""
        self.client.force_login(self.company)
        resp = self.client.get(reverse("transaction_history"))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Histórico de Transações")
        self.assertEqual(len(resp.context["transactions"]), 2)
        self.assertEqual(resp.context["total_purchases"], 2)
        self.assertEqual(resp.context["total_sales"], 0)

    def test_history_producer_sees_sales(self):
        """Produtor vê suas vendas no histórico."""
        self.client.force_login(self.producer)
        resp = self.client.get(reverse("transaction_history"))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["transactions"]), 2)
        self.assertEqual(resp.context["total_purchases"], 0)
        self.assertEqual(resp.context["total_sales"], 2)

    def test_history_empty_for_new_user(self):
        """Histórico vazio para usuário sem transações."""
        new_user = User.objects.create_user(
            username="newuser", password="pass123", role=User.Roles.COMPANY
        )
        self.client.force_login(new_user)
        resp = self.client.get(reverse("transaction_history"))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["transactions"]), 0)
        self.assertContains(resp, "ainda não tem transações")
