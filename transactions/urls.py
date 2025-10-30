"""URLs do app de transações."""

from django.urls import path

from . import views

urlpatterns = [
    # Histórico de transações (compras e vendas do usuário)
    path("", views.transaction_history, name="transaction_history"),

    # Public transactions page (no auth required)
    path("public/", views.public_transactions_view, name="public_transactions"),

    # SSE endpoint for real-time updates
    path("public/stream/", views.public_transactions_sse, name="public_transactions_sse"),
]

