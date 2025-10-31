from django.shortcuts import render
from django.http import JsonResponse
from credits.models import CarbonCredit

def credit_list(request):
    """API pública para listar créditos de carbono disponíveis"""
    credits = CarbonCredit.objects.filter(status='AVAILABLE').values(
        'id', 'amount', 'origin', 'generation_date', 'status', 'unit'
    )
    return JsonResponse(list(credits), safe=False)
