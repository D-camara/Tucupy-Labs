from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Health check
    path("_health/", views.placeholder, name="accounts_health"),

    # Autenticação
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # Perfil
    path("profile/", views.ProfileView.as_view(), name="profile"),
    
    # Saldo (apenas para empresas)
    path("add-balance/", views.add_balance_view, name="add_balance"),
]
