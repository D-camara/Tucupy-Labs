from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

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

    # Histórico de transações
    path("transactions/", include("transactions.urls")),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
