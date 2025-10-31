from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("_health/", views.placeholder, name="accounts_health"),

    # Auth
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # Cadastro principal (página base)
    path("register/", views.RegisterView.as_view(), name="register"),

    # Cadastro de Auditor (formulário funcional)
    path("auditors/register/", views.AuditorRegisterView.as_view(), name="auditor_register"),
]
