from django.http import HttpResponse
from django.shortcuts import render
from django.db import transaction
from .forms import TransactionForm


def placeholder(_request):
    return HttpResponse("transactions ok")

def compra_creditos(request):
    with transaction.atomic():
        form = TransactionForm()

        if request.method == "POST":
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.save
                return HttpResponse("Sucesso??")

#TODO - Logica de compra de creditos de Carbono
#       Atualizacao dinamica dos creditos de cada usuario no banco
#       
        return render(request, 'index.html', {'form' : form })