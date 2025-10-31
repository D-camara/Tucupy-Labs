from django.urls import path
from . import views
# Import da view de compra
from transactions.views import buy_credit

app_name = "credits"

urlpatterns = [
    # Página principal do marketplace (lista listagens ativas)
    path("", views.MarketplaceListView.as_view(), name="credits_marketplace"),
    # Criação de crédito (apenas produtores)
    path("create/", views.CreditCreateView.as_view(), name="credit_create"),
    # Detalhe do crédito
    path("<int:pk>/", views.CreditDetailView.as_view(), name="credit_detail"),
    # Histórico de propriedade (público - blockchain-style)
    path("<int:pk>/history/", views.credit_history, name="credit_history"),
    # Ação para listar um crédito para venda (apenas dono produtor)
    path("<int:pk>/list/", views.list_for_sale, name="credit_list_for_sale"),
    # Compra de crédito (apenas empresas - Company-only)
    path("<int:pk>/buy/", buy_credit, name="credit_buy"),
    
    # Auditoria (apenas auditores)
    path("audit/dashboard/", views.auditor_dashboard, name="auditor_dashboard"),
    path("audit/<int:pk>/review/", views.review_credit, name="review_credit"),
    path("audit/<int:pk>/view/", views.view_credit, name="view_credit"),
]

