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
        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "100.00"
            }),
            "origin": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "placeholder": "Ex: Fazenda Sustentável São Paulo"
            }),
            "generation_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition"
            }),
            "unit": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-tucupi-green-500 focus:ring-2 focus:ring-tucupi-green-500/50 focus:outline-none transition",
                "value": "tons CO2"
            }),
        }
        labels = {
            "amount": "Quantidade",
            "origin": "Origem",
            "generation_date": "Data de Geração",
            "unit": "Unidade",
        }


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
