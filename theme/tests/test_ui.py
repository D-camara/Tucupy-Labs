"""Testes de UI e Tailwind.

Este arquivo verifica:
- Renderização do base.html com Tailwind CSS
- Componentes navbar e credit_card
- Dashboard aplicando o layout base
- Classes CSS personalizadas (btn-primary, card, etc.)
"""

from __future__ import annotations

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class TailwindRenderingTests(TestCase):
    """Testes de renderização do Tailwind e componentes base."""

    def setUp(self):
        """Configura usuário para testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", role=User.Roles.PRODUCER
        )

    def test_base_template_loads_tailwind(self):
        """Template base.html carrega o CSS do Tailwind."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        # Verifica que o CSS foi injetado
        self.assertContains(resp, "/static/css/dist/styles.css")

    def test_navbar_component_renders(self):
        """Componente navbar.html é incluído e renderiza corretamente."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        # Verifica presença do navbar
        self.assertContains(resp, "Tucupi Labs")
        self.assertContains(resp, "Dashboard")
        self.assertContains(resp, "Marketplace")

    def test_dashboard_uses_base_template(self):
        """Dashboard utiliza o template base.html."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        # Verifica estrutura HTML do base.html
        self.assertContains(resp, '<html lang="pt-BR"')
        self.assertContains(resp, 'class="min-h-screen bg-tucupi-black text-white')
        self.assertContains(resp, '<main class="container mx-auto px-4 py-8">')

    def test_custom_css_classes_available(self):
        """Classes CSS personalizadas estão disponíveis (btn-primary, card, etc)."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        # Verifica uso de classes personalizadas no dashboard
        content = resp.content.decode()
        # Dashboard usa classes do Tailwind
        self.assertIn("glass", content)
        self.assertIn("rounded-lg", content)
        self.assertIn("tucupi-green", content)

    def test_marketplace_loads_with_tailwind(self):
        """Página do marketplace renderiza com Tailwind."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("credits_marketplace"))
        self.assertEqual(resp.status_code, 200)
        # Verifica que usa base.html
        self.assertContains(resp, "/static/css/dist/styles.css")
        self.assertContains(resp, "Tucupi Labs")

    def test_login_page_uses_tailwind_styles(self):
        """Página de login usa estilos do Tailwind."""
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "/static/css/dist/styles.css")
        # Verifica classes do Tailwind
        self.assertContains(resp, "bg-")
        self.assertContains(resp, "text-")

    def test_eco_theme_colors_configured(self):
        """Cores personalizadas eco-primary/secondary estão configuradas."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)
        # Verifica uso de cores verdes (tema eco)
        content = resp.content.decode()
        self.assertIn("tucupi-green", content)  # Classes personalizadas Tucupi Labs


class ComponentTests(TestCase):
    """Testes dos componentes reutilizáveis."""

    def setUp(self):
        """Configura usuário e crédito de teste."""
        self.user = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )
        self.client.force_login(self.user)

    def test_credit_card_component_structure(self):
        """Componente credit_card.html tem estrutura esperada."""
        # Lê o arquivo do componente
        from pathlib import Path
        import os
        
        base_dir = Path(__file__).resolve().parent.parent.parent
        component_path = base_dir / "templates" / "components" / "credit_card.html"
        
        self.assertTrue(component_path.exists(), "credit_card.html deve existir")
        
        content = component_path.read_text()
        # Verifica elementos essenciais (usa glass ao invés de credit-card)
        self.assertIn("glass", content)
        self.assertIn("{{ title", content)
        self.assertIn("{{ origin", content)
        self.assertIn("{{ amount", content)
        self.assertIn("{{ price", content)

    def test_navbar_has_required_links(self):
        """Navbar contém todos os links necessários."""
        from pathlib import Path
        
        base_dir = Path(__file__).resolve().parent.parent.parent
        navbar_path = base_dir / "templates" / "components" / "navbar.html"
        
        self.assertTrue(navbar_path.exists(), "navbar.html deve existir")
        
        content = navbar_path.read_text()
        # Verifica links essenciais (usa template tags ao invés de hardcoded)
        self.assertIn("{% url 'dashboard:index' %}", content)  # Dashboard
        self.assertIn("{% url 'credits_marketplace' %}", content)  # Marketplace
        self.assertIn("{% url 'public_transactions' %}", content)  # Transactions
        self.assertIn("{% url 'accounts:login' %}", content)  # Login
        self.assertIn("{% url 'accounts:register' %}", content)  # Register