"""Formulários do app de créditos.

Este módulo contém ModelForms usados para:
- Criar um novo CarbonCredit (pelo produtor)
- Criar uma CreditListing (listar um crédito para venda)
"""

from __future__ import annotations

from django import forms

from .models import CarbonCredit, CreditListing


class CarbonCreditForm(forms.ModelForm):
    """Formulário para cadastro de um novo crédito de carbono.

    Observação: o campo "owner" é definido na view com o usuário autenticado.
    """
    class Meta:
        model = CarbonCredit
        fields = [
            "amount",
            "origin",
            "generation_date",
            "unit",
        ]


class CreditListingForm(forms.ModelForm):
    """Formulário para criar uma listagem (anúncio) de um crédito.

    Somente o preço por unidade é informado aqui; o vínculo com o
    crédito específico é feito na view.
    """
    class Meta:
        model = CreditListing
        fields = [
            "price_per_unit",
        ]
