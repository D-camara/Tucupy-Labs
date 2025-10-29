from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin do Django
    path("admin/", admin.site.urls),

    # Página inicial/dashboards
    path("", include("dashboard.urls")),

    # Auto-reload em desenvolvimento (injetado pelo middleware)
    path("__reload__/", include("django_browser_reload.urls")),

    # Autenticação/contas
    path("accounts/", include("accounts.urls")),

    # Marketplace e créditos
    path("credits/", include("credits.urls")),

    # Compras/transferências (a implementar)
    # path("transactions/", include("transactions.urls")),
]
