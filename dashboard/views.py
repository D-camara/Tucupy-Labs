from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from credits.models import CarbonCredit, CreditListing
from transactions.models import Transaction
from django.db.models import Sum

@login_required
def index(request):
    user = request.user
    context = {}
    
    # Carteira (comum a todos os usuários)
    context['my_credits'] = CarbonCredit.objects.filter(
        owner=user, 
        status='AVAILABLE'
    ).aggregate(
        total_amount=Sum('amount')
    )['total_amount'] or 0
    
    # Últimas 5 transações do usuário
    context['recent_transactions'] = Transaction.objects.filter(
        buyer=user
    ).order_by('-timestamp')[:5]
    
    if user.role == 'PRODUCER':
        # Dados específicos do produtor
        context['listed_credits'] = CreditListing.objects.filter(
            credit__owner=user,
            is_active=True
        ).count()
        context['total_sales'] = Transaction.objects.filter(
            seller=user,
            status='COMPLETED'
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
    elif user.role == 'COMPANY':
        # Dados específicos da empresa
        context['available_credits'] = CreditListing.objects.filter(
            is_active=True
        ).count()
        context['total_purchased'] = Transaction.objects.filter(
            buyer=user,
            status='COMPLETED'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
    
    return render(request, "dashboard/index.html", context)
