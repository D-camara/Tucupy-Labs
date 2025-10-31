"""
Módulo de utilitários para envio de emails.

Funções helper para envio de emails relacionados ao sistema de auditoria
e notificações gerais da plataforma EcoTrade.
"""

from typing import List, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_html_email(
    subject: str,
    template_name: str,
    context: dict,
    recipient_list: List[str],
    from_email: Optional[str] = None,
) -> int:
    """
    Envia email HTML usando template Django.
    
    Args:
        subject: Assunto do email
        template_name: Nome do template HTML (ex: 'emails/welcome.html')
        context: Dicionário com variáveis para o template
        recipient_list: Lista de emails destinatários
        from_email: Email remetente (usa DEFAULT_FROM_EMAIL se None)
    
    Returns:
        Número de emails enviados com sucesso
    
    Example:
        send_html_email(
            subject='Bem-vindo ao EcoTrade',
            template_name='emails/welcome.html',
            context={'user_name': 'João'},
            recipient_list=['joao@example.com']
        )
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Renderiza o template HTML
    html_content = render_to_string(template_name, context)
    
    # Cria versão texto simples (fallback)
    text_content = strip_tags(html_content)
    
    # Cria email com versões HTML e texto
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    
    return email.send()


def send_auditor_application_confirmation(user_email: str, user_name: str) -> int:
    """
    Envia email de confirmação de candidatura a auditor.
    
    Args:
        user_email: Email do candidato
        user_name: Nome do candidato
    
    Returns:
        Número de emails enviados (1 se sucesso, 0 se falha)
    """
    return send_html_email(
        subject='EcoTrade - Candidatura Recebida',
        template_name='emails/auditor_application_received.html',
        context={
            'user_name': user_name,
        },
        recipient_list=[user_email],
    )


def send_auditor_approval_notification(user_email: str, user_name: str) -> int:
    """
    Envia email de aprovação de candidatura a auditor.
    
    Args:
        user_email: Email do candidato aprovado
        user_name: Nome do candidato
    
    Returns:
        Número de emails enviados
    """
    return send_html_email(
        subject='EcoTrade - Candidatura Aprovada! 🎉',
        template_name='emails/auditor_approved.html',
        context={
            'user_name': user_name,
        },
        recipient_list=[user_email],
    )


def send_auditor_rejection_notification(
    user_email: str,
    user_name: str,
    reason: Optional[str] = None
) -> int:
    """
    Envia email de rejeição de candidatura a auditor.
    
    Args:
        user_email: Email do candidato rejeitado
        user_name: Nome do candidato
        reason: Motivo da rejeição (opcional)
    
    Returns:
        Número de emails enviados
    """
    return send_html_email(
        subject='EcoTrade - Status da Candidatura',
        template_name='emails/auditor_rejected.html',
        context={
            'user_name': user_name,
            'reason': reason or 'Infelizmente não pudemos aprovar sua candidatura no momento.',
        },
        recipient_list=[user_email],
    )


def send_admin_new_application_notification(
    admin_emails: List[str],
    applicant_name: str,
    applicant_email: str,
    application_id: int
) -> int:
    """
    Notifica administradores sobre nova candidatura a auditor.
    
    Args:
        admin_emails: Lista de emails dos administradores
        applicant_name: Nome do candidato
        applicant_email: Email do candidato
        application_id: ID da candidatura
    
    Returns:
        Número de emails enviados
    """
    return send_html_email(
        subject=f'Nova Candidatura a Auditor - {applicant_name}',
        template_name='emails/admin_new_application.html',
        context={
            'applicant_name': applicant_name,
            'applicant_email': applicant_email,
            'application_id': application_id,
        },
        recipient_list=admin_emails,
    )


def send_credit_validation_request(
    auditor_email: str,
    auditor_name: str,
    credit_id: int,
    credit_title: str,
    producer_name: str,
) -> int:
    """
    Notifica auditor sobre novo crédito aguardando validação.
    
    Args:
        auditor_email: Email do auditor
        auditor_name: Nome do auditor
        credit_id: ID do crédito
        credit_title: Título do crédito
        producer_name: Nome do produtor
    
    Returns:
        Número de emails enviados
    """
    return send_html_email(
        subject=f'Novo Crédito para Validação - {credit_title}',
        template_name='emails/credit_validation_request.html',
        context={
            'auditor_name': auditor_name,
            'credit_id': credit_id,
            'credit_title': credit_title,
            'producer_name': producer_name,
        },
        recipient_list=[auditor_email],
    )


def send_credit_validation_result(
    producer_email: str,
    producer_name: str,
    credit_title: str,
    approved: bool,
    auditor_notes: Optional[str] = None,
) -> int:
    """
    Notifica produtor sobre resultado da validação do crédito.
    
    Args:
        producer_email: Email do produtor
        producer_name: Nome do produtor
        credit_title: Título do crédito
        approved: True se aprovado, False se rejeitado
        auditor_notes: Observações do auditor (opcional)
    
    Returns:
        Número de emails enviados
    """
    subject = f'Crédito {"Aprovado" if approved else "Rejeitado"} - {credit_title}'
    template = 'emails/credit_approved.html' if approved else 'emails/credit_rejected.html'
    
    return send_html_email(
        subject=subject,
        template_name=template,
        context={
            'producer_name': producer_name,
            'credit_title': credit_title,
            'auditor_notes': auditor_notes or '',
        },
        recipient_list=[producer_email],
    )
