"""URLs da API pública."""

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'api'

urlpatterns = [
    # Documentação da API (página HTML interativa)
    path('', TemplateView.as_view(template_name='api_docs.html'), name='docs'),
    
    # Lista de créditos
    path('credits/', views.credits_list, name='credits_list'),
    
    # Detalhe de crédito específico
    path('credits/<int:credit_id>/', views.credit_detail, name='credit_detail'),
    
    # Estatísticas públicas
    path('stats/', views.stats, name='stats'),
]
