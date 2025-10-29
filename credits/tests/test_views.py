from __future__ import annotations

"""Testes do fluxo de Créditos e Marketplace.

Este arquivo cobre:
- Permissões para criar crédito (Producer-only)
- Listagem para venda (validações e efeitos colaterais)
- Filtro do marketplace (apenas ativos e LISTED) + paginação
- Renderização da página de detalhe
"""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from credits.models import CarbonCredit, CreditListing


class CreditsMarketplaceTests(TestCase):
    def setUp(self) -> None:
        """Cria usuários de teste para simular papéis do sistema."""
        self.producer = User.objects.create_user(
            username="producer1", password="pass12345", role=User.Roles.PRODUCER
        )
        self.producer2 = User.objects.create_user(
            username="producer2", password="pass12345", role=User.Roles.PRODUCER
        )
        self.company = User.objects.create_user(
            username="company1", password="pass12345", role=User.Roles.COMPANY
        )

    def create_credit(self, owner: User | None = None) -> CarbonCredit:
        """Helper para criar um crédito pronto para uso nos testes."""
        return CarbonCredit.objects.create(
            owner=owner or self.producer,
            amount=10,
            origin="Test Farm",
            generation_date=date(2025, 1, 1),
            status=CarbonCredit.Status.AVAILABLE,
            unit="tons CO2",
        )

    def test_create_credit_requires_producer_role(self):
        """Somente produtor pode acessar/usar a tela de criação de crédito."""
        self.client.force_login(self.company)
        url = reverse("credit_create")
        # GET should be forbidden for non-producer
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 403)
        # POST should be forbidden for non-producer
        resp_post = self.client.post(
            url,
            {
                "amount": 5,
                "origin": "Company Farm",
                "generation_date": "2025-01-01",
                "unit": "tons CO2",
            },
        )
        self.assertEqual(resp_post.status_code, 403)

    def test_create_credit_success_by_producer(self):
        """Produtor consegue criar crédito com sucesso e é redirecionado ao detalhe."""
        self.client.force_login(self.producer)
        url = reverse("credit_create")
        resp = self.client.post(
            url,
            {
                "amount": 12.5,
                "origin": "Green Ranch",
                "generation_date": "2025-02-10",
                "unit": "tons CO2",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        # Redirected to detail
        self.assertIn("/credits/", resp.request["PATH_INFO"])  # detail view
        credit = CarbonCredit.objects.get(origin="Green Ranch")
        self.assertEqual(credit.owner, self.producer)
        self.assertEqual(credit.status, CarbonCredit.Status.AVAILABLE)

    def test_list_for_sale_requires_owner_producer(self):
        """Apenas o produtor dono do crédito pode listar para venda."""
        credit = self.create_credit(owner=self.producer)
        self.client.force_login(self.producer2)
        url = reverse("credit_list_for_sale", args=[credit.pk])
        resp = self.client.post(url, {"price_per_unit": 100})
        self.assertEqual(resp.status_code, 403)

    def test_list_for_sale_sets_status_listed_and_creates_listing(self):
        """Listar cria a CreditListing e atualiza status do crédito para LISTED."""
        credit = self.create_credit(owner=self.producer)
        self.client.force_login(self.producer)
        url = reverse("credit_list_for_sale", args=[credit.pk])
        resp = self.client.post(url, {"price_per_unit": 99.99}, follow=True)
        self.assertEqual(resp.status_code, 200)
        credit.refresh_from_db()
        self.assertEqual(credit.status, CarbonCredit.Status.LISTED)
        self.assertTrue(CreditListing.objects.filter(credit=credit, is_active=True).exists())

    def test_list_for_sale_prevents_duplicate_active_listings(self):
        """Impede múltiplas listagens ativas para o mesmo crédito."""
        credit = self.create_credit(owner=self.producer)
        # First listing
        CreditListing.objects.create(credit=credit, price_per_unit=50, is_active=True)
        credit.status = CarbonCredit.Status.LISTED
        credit.save(update_fields=["status"])

        self.client.force_login(self.producer)
        url = reverse("credit_list_for_sale", args=[credit.pk])
        resp = self.client.post(url, {"price_per_unit": 60})
        # Should render form with error (no redirect)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode("utf-8")
        # Depending on validation order, we may see either of these messages
        self.assertTrue(
            ("Já existe uma listagem ativa para este crédito." in content)
            or ("Este crédito não está disponível para listagem." in content)
        )
        self.assertEqual(CreditListing.objects.filter(credit=credit, is_active=True).count(), 1)

    def test_marketplace_shows_only_active_listed(self):
        """Marketplace deve exibir apenas listagens ativas com crédito LISTED."""
        # Active listed credit
        credit1 = self.create_credit(owner=self.producer)
        CreditListing.objects.create(credit=credit1, price_per_unit=10, is_active=True)
        credit1.status = CarbonCredit.Status.LISTED
        credit1.save(update_fields=["status"])
        # Inactive listing shouldn't show
        credit2 = self.create_credit(owner=self.producer)
        CreditListing.objects.create(credit=credit2, price_per_unit=20, is_active=False)
        credit2.status = CarbonCredit.Status.LISTED
        credit2.save(update_fields=["status"])

        # SOLD credit shouldn't show even if listing set (defensive)
        credit3 = self.create_credit(owner=self.producer)
        CreditListing.objects.create(credit=credit3, price_per_unit=30, is_active=True)
        credit3.status = CarbonCredit.Status.SOLD
        credit3.save(update_fields=["status"])

        resp = self.client.get(reverse("credits_marketplace"))
        self.assertEqual(resp.status_code, 200)
        listings = list(resp.context["listings"])  # type: ignore[index]
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].credit, credit1)

    def test_marketplace_pagination(self):
        """Paginação de 10 itens por página no marketplace."""
        for i in range(11):
            c = self.create_credit(owner=self.producer)
            CreditListing.objects.create(credit=c, price_per_unit=10 + i, is_active=True)
            c.status = CarbonCredit.Status.LISTED
            c.save(update_fields=["status"])

        resp1 = self.client.get(reverse("credits_marketplace"))
        self.assertEqual(resp1.status_code, 200)
        self.assertTrue(resp1.context["is_paginated"])  # type: ignore[index]
        self.assertEqual(len(resp1.context["listings"]), 10)  # type: ignore[index]

        resp2 = self.client.get(reverse("credits_marketplace") + "?page=2")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.context["listings"]), 1)  # type: ignore[index]

    def test_credit_detail_page_loads(self):
        """Página de detalhe deve renderizar e conter dados do crédito."""
        credit = self.create_credit(owner=self.producer)
        resp = self.client.get(reverse("credit_detail", args=[credit.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, str(credit.amount))
        self.assertContains(resp, credit.origin)
