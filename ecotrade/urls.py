from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Admin do Django
    path("admin/", admin.site.urls),
    # Página inicial/dashboards
    path("", include("dashboard.urls")),
    # Auto-reload em desenvolvimento (injetado pelo middleware)
    path("__reload__/", include("django_browser_reload.urls")),
    # URLs das apps do projeto
    # path("accounts/", include("accounts.urls")),  # Autenticação/contas (a implementar)
    path("credits/", include("credits.urls")),      # Marketplace e créditos
    # path("transactions/", include("transactions.urls")),  # Compras/transferências (a implementar)
]
