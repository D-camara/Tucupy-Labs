from django.urls import path
from . import views


urlpatterns = [
    # Página principal do marketplace (lista listagens ativas)
    path("", views.MarketplaceListView.as_view(), name="credits_marketplace"),
    # Criação de crédito (apenas produtores)
    path("create/", views.CreditCreateView.as_view(), name="credit_create"),
    # Detalhe do crédito
    path("<int:pk>/", views.CreditDetailView.as_view(), name="credit_detail"),
    # Ação para listar um crédito para venda (apenas dono produtor)
    path("<int:pk>/list/", views.list_for_sale, name="credit_list_for_sale"),
]

