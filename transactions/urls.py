"""URLs do app de transações."""

from django.urls import path

from . import views

urlpatterns = [
    # Histórico de transações (compras e vendas do usuário)
    path("", views.transaction_history, name="transaction_history"),
]

