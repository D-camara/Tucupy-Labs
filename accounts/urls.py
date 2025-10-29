from django.urls import path
from . import views


urlpatterns = [
    path("_health/", views.placeholder, name="accounts_health"),
]

