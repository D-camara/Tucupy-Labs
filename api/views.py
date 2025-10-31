"""
API pública para consulta de créditos de carbono.
Promove transparência permitindo consulta pública dos créditos registrados.
"""

from __future__ import annotations

import json
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from credits.models import CarbonCredit


@require_http_methods(["GET"])
def credits_list(request: HttpRequest) -> JsonResponse:
    """
    Lista todos os créditos de carbono registrados no sistema.
    
    Endpoint público que promove transparência.
    Retorna apenas créditos aprovados e não deletados.
    
    Query params:
        - status: filtrar por status (AVAILABLE, LISTED, SOLD)
        - validation_status: filtrar por status de validação (APPROVED, PENDING, etc)
        - limit: número máximo de resultados (padrão: 100, máx: 500)
        - offset: pular N primeiros resultados (para paginação)
    
    Exemplo:
        GET /api/credits/?status=LISTED&limit=10
    """
    # Filtrar apenas créditos aprovados e não deletados (transparência de dados confiáveis)
    queryset: QuerySet[CarbonCredit] = CarbonCredit.objects.filter(
        validation_status=CarbonCredit.ValidationStatus.APPROVED,
        is_deleted=False
    ).select_related('owner', 'validated_by')
    
    # Filtros opcionais
    status = request.GET.get('status')
    if status and status in [choice[0] for choice in CarbonCredit.Status.choices]:
        queryset = queryset.filter(status=status)
    
    validation_status = request.GET.get('validation_status')
    if validation_status and validation_status in [choice[0] for choice in CarbonCredit.ValidationStatus.choices]:
        queryset = queryset.filter(validation_status=validation_status)
    
    # Paginação
    try:
        limit = min(int(request.GET.get('limit', 100)), 500)  # máximo 500
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        limit = 100
        offset = 0
    
    total_count = queryset.count()
    queryset = queryset[offset:offset + limit]
    
    # Serializar dados
    credits_data = []
    for credit in queryset:
        credits_data.append({
            'id': credit.id,
            'amount': float(credit.amount),
            'unit': credit.unit,
            'origin': credit.origin,
            'generation_date': credit.generation_date.isoformat(),
            'status': credit.status,
            'validation_status': credit.validation_status,
            'owner': {
                'username': credit.owner.username,
                'role': credit.owner.role,
            },
            'validated_by': {
                'username': credit.validated_by.username if credit.validated_by else None,
            } if credit.validated_by else None,
            'validated_at': credit.validated_at.isoformat() if credit.validated_at else None,
            'created_at': credit.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'count': len(credits_data),
        'total': total_count,
        'limit': limit,
        'offset': offset,
        'next_offset': offset + limit if offset + limit < total_count else None,
        'data': credits_data,
    })


@require_http_methods(["GET"])
def credit_detail(request: HttpRequest, credit_id: int) -> JsonResponse:
    """
    Retorna detalhes de um crédito específico.
    
    Endpoint público para consulta de crédito individual.
    Retorna apenas se aprovado e não deletado.
    
    Args:
        credit_id: ID do crédito
    
    Exemplo:
        GET /api/credits/123/
    """
    try:
        credit = CarbonCredit.objects.select_related(
            'owner', 'validated_by'
        ).get(
            id=credit_id,
            validation_status=CarbonCredit.ValidationStatus.APPROVED,
            is_deleted=False
        )
    except CarbonCredit.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Crédito não encontrado ou não disponível publicamente.',
        }, status=404)
    
    # Dados detalhados
    data = {
        'id': credit.id,
        'amount': float(credit.amount),
        'unit': credit.unit,
        'origin': credit.origin,
        'generation_date': credit.generation_date.isoformat(),
        'status': credit.status,
        'validation_status': credit.validation_status,
        'is_verified': credit.is_verified,
        'owner': {
            'username': credit.owner.username,
            'role': credit.owner.role,
        },
        'validated_by': {
            'username': credit.validated_by.username if credit.validated_by else None,
        } if credit.validated_by else None,
        'validated_at': credit.validated_at.isoformat() if credit.validated_at else None,
        'auditor_notes': credit.auditor_notes if credit.auditor_notes else None,
        'created_at': credit.created_at.isoformat(),
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
    })


@require_http_methods(["GET"])
def stats(request: HttpRequest) -> JsonResponse:
    """
    Retorna estatísticas públicas do sistema.
    
    Promove transparência mostrando números gerais.
    
    Exemplo:
        GET /api/stats/
    """
    from django.db.models import Sum
    from accounts.models import User
    from transactions.models import Transaction
    
    approved_credits = CarbonCredit.objects.filter(
        validation_status=CarbonCredit.ValidationStatus.APPROVED,
        is_deleted=False
    )
    
    total_co2 = approved_credits.aggregate(total=Sum('amount'))['total'] or 0
    
    stats_data = {
        'total_credits_registered': approved_credits.count(),
        'total_co2_amount': float(total_co2),
        'credits_available': approved_credits.filter(status=CarbonCredit.Status.AVAILABLE).count(),
        'credits_listed': approved_credits.filter(status=CarbonCredit.Status.LISTED).count(),
        'credits_sold': approved_credits.filter(status=CarbonCredit.Status.SOLD).count(),
        'total_producers': User.objects.filter(role=User.Roles.PRODUCER).count(),
        'total_companies': User.objects.filter(role=User.Roles.COMPANY).count(),
        'total_transactions': Transaction.objects.filter(status=Transaction.Status.COMPLETED).count(),
    }
    
    return JsonResponse({
        'success': True,
        'data': stats_data,
    })
