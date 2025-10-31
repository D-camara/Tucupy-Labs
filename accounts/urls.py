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
    
    # Candidatura de auditor
    path("auditor/apply/", views.auditor_application_view, name="auditor_apply"),
    
    # Admin dashboard
    path("admin/dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin/auditor/<int:pk>/approve/", views.approve_auditor_view, name="approve_auditor"),
    path("admin/auditor/<int:pk>/reject/", views.reject_auditor_view, name="reject_auditor"),
]
