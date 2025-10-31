from django.urls import path
from . import views

urlpatterns = [
    path('credits/', views.credit_list, name='api_credits'),
]