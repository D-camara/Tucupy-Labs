"""Testes do fluxo de Autenticação e Perfil.

Este arquivo cobre:
- Registro de novos usuários com escolha de papel (Producer/Company)
- Login e logout
- Edição de perfil (Profile model)
- Mixins/decorators RBAC (Producer/Company)
- Proteção de rotas por autenticação
"""

from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from accounts.models import User, Profile


class AuthenticationTests(TestCase):
    """Testes de autenticação: registro, login, logout."""

    def test_register_page_loads(self):
        """Página de registro carrega corretamente."""
        resp = self.client.get(reverse("accounts:register"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Crie sua conta")

    def test_register_creates_user_and_logs_in(self):
        """Registrar novo usuário cria conta e faz login automaticamente."""
        data = {
            "username": "testproducer",
            "email": "producer@test.com",
            "role": User.Roles.PRODUCER,
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        resp = self.client.post(reverse("accounts:register"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        
        # Usuário criado no banco
        user = User.objects.get(username="testproducer")
        self.assertEqual(user.email, "producer@test.com")
        self.assertEqual(user.role, User.Roles.PRODUCER)
        
        # Usuário logado automaticamente
        self.assertTrue(resp.wsgi_request.user.is_authenticated)
        self.assertEqual(resp.wsgi_request.user.username, "testproducer")

    def test_admin_role_not_available_in_public_registration(self):
        """Papel ADMIN não está disponível no registro público."""
        # Tentar registrar como ADMIN não deve funcionar
        data = {
            "username": "adminuser",
            "email": "admin@test.com",
            "role": User.Roles.ADMIN,  # Tentar forçar ADMIN
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        resp = self.client.post(reverse("accounts:register"), data)
        
        # Form deve rejeitar (ADMIN não está nas choices)
        self.assertEqual(resp.status_code, 200)  # Volta ao form com erro
        self.assertContains(resp, "Select a valid choice")
        
        # Usuário não foi criado
        self.assertFalse(User.objects.filter(username="adminuser").exists())
        
    def test_only_producer_and_company_roles_available(self):
        """Apenas roles PRODUCER e COMPANY estão disponíveis no formulário público."""
        resp = self.client.get(reverse("accounts:register"))
        content = resp.content.decode()
        
        # Deve conter opções de Produtor e Empresa
        self.assertIn("Produtor", content)
        self.assertIn("Empresa", content)
        
        # Não deve mencionar Admin como opção
        self.assertNotIn("Acesso administrativo", content)

    def test_register_company_user(self):
        """Registrar usuário com papel COMPANY."""
        data = {
            "username": "testcompany",
            "email": "company@test.com",
            "role": User.Roles.COMPANY,
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        resp = self.client.post(reverse("accounts:register"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        
        user = User.objects.get(username="testcompany")
        self.assertEqual(user.role, User.Roles.COMPANY)

    def test_login_page_loads(self):
        """Página de login carrega corretamente."""
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Entrar")

    def test_login_with_valid_credentials(self):
        """Login com credenciais válidas autentica usuário."""
        user = User.objects.create_user(
            username="testuser", password="TestPass123!", role=User.Roles.PRODUCER
        )
        
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "TestPass123!"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)
        self.assertEqual(resp.wsgi_request.user.username, "testuser")

    def test_login_with_invalid_credentials(self):
        """Login com credenciais inválidas não autentica."""
        User.objects.create_user(
            username="testuser", password="TestPass123!", role=User.Roles.PRODUCER
        )
        
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "WrongPassword"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)
        # Formulário deve mostrar erro personalizado
        self.assertContains(resp, "Nome de usuário ou senha incorretos")

    def test_logout_logs_out_user(self):
        """Logout desautentica o usuário."""
        user = User.objects.create_user(
            username="testuser", password="TestPass123!", role=User.Roles.PRODUCER
        )
        self.client.force_login(user)
        
        resp = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)


class ProfileTests(TestCase):
    """Testes de perfil: edição e criação automática."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", role=User.Roles.PRODUCER
        )

    def test_profile_page_requires_login(self):
        """Página de perfil redireciona se não autenticado."""
        resp = self.client.get(reverse("accounts:profile"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_profile_page_loads_for_authenticated_user(self):
        """Página de perfil carrega para usuário autenticado."""
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:profile"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Meu Perfil")

    def test_profile_auto_created_on_access(self):
        """Profile é criado automaticamente via signal quando User é criado."""
        self.client.force_login(self.user)
        # Como há um signal post_save que cria Profile automaticamente,
        # verificamos que o profile já existe após criar o usuário
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        
        resp = self.client.get(reverse("accounts:profile"))
        self.assertEqual(resp.status_code, 200)
        
        # Profile continua existindo
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_edit_profile_updates_fields(self):
        """Editar perfil atualiza os campos corretamente."""
        self.client.force_login(self.user)
        
        data = {
            "company_name": "",
            "farm_name": "Green Farm",
            "location": "São Paulo, SP",
            "tax_id": "12345678900",
            "phone": "+55 11 98765-4321",
        }
        resp = self.client.post(reverse("accounts:profile"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.farm_name, "Green Farm")
        self.assertEqual(profile.location, "São Paulo, SP")
        self.assertEqual(profile.tax_id, "12345678900")
        self.assertEqual(profile.phone, "+55 11 98765-4321")


class RBACTests(TestCase):
    """Testes dos mixins e decorators de RBAC."""

    def setUp(self):
        self.producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )
        self.company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )

    def test_producer_can_create_credit(self):
        """Producer consegue acessar tela de criar crédito."""
        self.client.force_login(self.producer)
        resp = self.client.get(reverse("credits:credit_create"))
        self.assertEqual(resp.status_code, 200)

    def test_company_cannot_create_credit(self):
        """Company recebe 403 ao tentar criar crédito."""
        self.client.force_login(self.company)
        resp = self.client.get(reverse("credits:credit_create"))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_cannot_create_credit(self):
        """Usuário não autenticado recebe 403 ou redirecionamento ao tentar criar crédito."""
        resp = self.client.get(reverse("credits:credit_create"))
        # Pode ser 403 (PermissionDenied) ou 302 (redirecionamento para LoginRequired)
        self.assertIn(resp.status_code, [302, 403])


class AdminAccessTests(TestCase):
    """Testes da propriedade is_admin e acesso ao dashboard."""

    def test_superuser_is_admin(self):
        """Superuser deve ter is_admin=True."""
        superuser = User.objects.create_superuser(
            username="super", password="pass123", email="super@test.com"
        )
        self.assertTrue(superuser.is_admin)
        # Signal deve ter atribuído role ADMIN automaticamente
        superuser.refresh_from_db()
        self.assertEqual(superuser.role, User.Roles.ADMIN)

    def test_admin_role_is_admin(self):
        """Usuário com role ADMIN deve ter is_admin=True."""
        admin = User.objects.create_user(
            username="admin", password="pass123", role=User.Roles.ADMIN
        )
        self.assertTrue(admin.is_admin)

    def test_regular_user_not_admin(self):
        """Usuário comum (producer/company) não deve ter is_admin=True."""
        producer = User.objects.create_user(
            username="producer", password="pass123", role=User.Roles.PRODUCER
        )
        company = User.objects.create_user(
            username="company", password="pass123", role=User.Roles.COMPANY
        )
        self.assertFalse(producer.is_admin)
        self.assertFalse(company.is_admin)
