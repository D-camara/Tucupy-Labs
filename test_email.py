#!/usr/bin/env python
"""Script para testar configuração de email."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecotrade.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("🧪 TESTE DE CONFIGURAÇÃO DE EMAIL")
print("=" * 60)
print(f"\n📧 Email configurado: {settings.EMAIL_HOST_USER}")
print(f"📮 Servidor SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"🔒 TLS: {'Sim' if settings.EMAIL_USE_TLS else 'Não'}")
print("\n" + "=" * 60)

# Pedir email de destino
email_destino = input("\n📩 Digite o email para testar (ou Enter para usar tucupilabs@gmail.com): ").strip()
if not email_destino:
    email_destino = 'tucupilabs@gmail.com'

print(f"\n🚀 Enviando email de teste para: {email_destino}")
print("⏳ Aguarde...")

try:
    send_mail(
        subject='✅ Teste de Email - EcoTrade Platform',
        message='''
Olá!

Este é um email de teste da plataforma EcoTrade - Tucupi Labs.

Se você recebeu este email, significa que a configuração está funcionando perfeitamente! 🎉

🌱 EcoTrade Platform
💚 Tucupi Labs
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_destino],
        fail_silently=False,
    )
    
    print("\n" + "=" * 60)
    print("✅ EMAIL ENVIADO COM SUCESSO!")
    print("=" * 60)
    print(f"\n📬 Verifique a caixa de entrada de: {email_destino}")
    print("⚠️  Não esquece de verificar a pasta de SPAM também!")
    print("\n" + "=" * 60 + "\n")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ ERRO AO ENVIAR EMAIL")
    print("=" * 60)
    print(f"\n⚠️  Erro: {str(e)}")
    print("\n💡 Possíveis causas:")
    print("   - Senha de app incorreta")
    print("   - Firewall bloqueando porta 587")
    print("   - Autenticação de 2 fatores não ativada")
    print("   - Verificação em duas etapas não configurada")
    print("\n" + "=" * 60 + "\n")
