from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    # Future: add app URLs as implemented
    path("accounts/", include("accounts.urls")),
    # path("credits/", include("credits.urls")),
    # path("transactions/", include("transactions.urls")),
]
