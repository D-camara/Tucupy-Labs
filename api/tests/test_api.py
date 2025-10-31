"""Testes da API pública."""

import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from credits.models import CarbonCredit

User = get_user_model()


class PublicAPITests(TestCase):
    """Testes dos endpoints públicos da API."""

    def setUp(self):
        """Configura dados para testes."""
        self.client = Client()

        # Criar produtor
        self.producer = User.objects.create_user(
            username="producer1",
            password="pass123",
            role=User.Roles.PRODUCER
        )

        # Criar auditor
        self.auditor = User.objects.create_user(
            username="auditor1",
            password="pass123",
            role=User.Roles.AUDITOR
        )

        # Criar crédito aprovado (visível na API)
        self.approved_credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("100.00"),
            origin="Fazenda Teste",
            generation_date="2025-10-01",
            status=CarbonCredit.Status.AVAILABLE,
            validation_status=CarbonCredit.ValidationStatus.APPROVED,
            validated_by=self.auditor,
        )

        # Criar crédito pendente (não visível na API)
        self.pending_credit = CarbonCredit.objects.create(
            owner=self.producer,
            amount=Decimal("50.00"),
            origin="Fazenda Teste 2",
            generation_date="2025-10-15",
            status=CarbonCredit.Status.AVAILABLE,
            validation_status=CarbonCredit.ValidationStatus.PENDING,
        )

    def test_stats_endpoint(self):
        """Testa endpoint de estatísticas."""
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('total_credits_registered', data['data'])
        self.assertIn('total_co2_amount', data['data'])

    def test_credits_list_endpoint(self):
        """Testa listagem de créditos."""
        response = self.client.get('/api/credits/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)  # Apenas approved
        self.assertEqual(len(data['data']), 1)
        
        # Verificar estrutura do crédito
        credit = data['data'][0]
        self.assertIn('id', credit)
        self.assertIn('amount', credit)
        self.assertIn('origin', credit)
        self.assertIn('validation_status', credit)
        self.assertEqual(credit['validation_status'], 'APPROVED')

    def test_credits_list_only_shows_approved(self):
        """Testa que apenas créditos aprovados aparecem na lista."""
        response = self.client.get('/api/credits/')
        data = json.loads(response.content)
        
        # Deve ter apenas 1 crédito (o aprovado)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['origin'], "Fazenda Teste")

    def test_credits_list_with_filters(self):
        """Testa filtros da listagem."""
        response = self.client.get('/api/credits/?status=AVAILABLE')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Todos devem ter status AVAILABLE
        for credit in data['data']:
            self.assertEqual(credit['status'], 'AVAILABLE')

    def test_credits_list_pagination(self):
        """Testa paginação."""
        response = self.client.get('/api/credits/?limit=1&offset=0')
        data = json.loads(response.content)
        
        self.assertEqual(data['limit'], 1)
        self.assertEqual(data['offset'], 0)
        self.assertIn('next_offset', data)

    def test_credit_detail_endpoint(self):
        """Testa endpoint de detalhe do crédito."""
        response = self.client.get(f'/api/credits/{self.approved_credit.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        credit = data['data']
        self.assertEqual(credit['origin'], "Fazenda Teste")
        self.assertEqual(credit['validation_status'], 'APPROVED')
        self.assertIn('validated_by', credit)
        self.assertEqual(credit['validated_by']['username'], 'auditor1')

    def test_credit_detail_not_found(self):
        """Testa que crédito não aprovado retorna 404."""
        response = self.client.get(f'/api/credits/{self.pending_credit.id}/')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_credit_detail_invalid_id(self):
        """Testa ID inválido."""
        response = self.client.get('/api/credits/99999/')
        self.assertEqual(response.status_code, 404)

    def test_api_docs_page(self):
        """Testa que a página de documentação carrega."""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Pública EcoTrade')
