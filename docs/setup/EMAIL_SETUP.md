# 📧 Configuração de Email - Tucupi Labs

## Desenvolvimento (Console Backend)

Por padrão, o projeto está configurado para usar o **Console Backend** em desenvolvimento. Isso significa que os emails não são enviados de verdade, mas sim impressos no terminal onde o servidor Django está rodando.

**Vantagens:**
- ✅ Não precisa de configuração externa
- ✅ Rápido para testar
- ✅ Sem necessidade de senha ou credenciais

**Como funciona:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Quando um email for enviado, você verá algo assim no terminal:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Candidatura Aprovada
From: Tucupi Labs <tucupilabs@gmail.com>
To: candidato@example.com
Date: Wed, 30 Oct 2025 12:00:00 -0000

Olá João,

Sua candidatura foi aprovada!
...
```

---

## Produção (Gmail SMTP)

Para enviar emails **reais em produção**, você precisa configurar o Gmail SMTP.

### 📋 Passo a Passo:

#### 1. Criar Senha de App no Gmail

O Gmail não permite mais usar a senha normal da conta. Você precisa criar uma **Senha de App**.

**Passos:**

1. Acesse sua conta Google: https://myaccount.google.com/
2. Vá em **Segurança** (no menu lateral)
3. Ative a **Verificação em duas etapas** (se ainda não estiver ativada)
4. Depois de ativar, volte em **Segurança**
5. Role até encontrar **Senhas de app** (pode estar em "Como fazer login no Google")
6. Clique em **Senhas de app**
7. Selecione:
   - **App**: Outro (nome personalizado)
   - **Nome**: Digite "Django - Tucupi Labs"
8. Clique em **Gerar**
9. O Google mostrará uma senha de 16 caracteres (ex: `abcd efgh ijkl mnop`)
10. **Copie essa senha** (sem espaços)

**Importante:** 
- ⚠️ Essa senha só aparece uma vez!
- ⚠️ Guarde em local seguro
- ⚠️ Não compartilhe com ninguém

#### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (copie de `.env.example`):

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Email Configuration para PRODUÇÃO
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucupilabs@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # Cole a senha de app AQUI (sem espaços)

DEFAULT_FROM_EMAIL=Tucupi Labs <tucupilabs@gmail.com>
SITE_URL=http://localhost:8000  # Ou URL de produção
```

#### 3. Instalar python-dotenv (se necessário)

```bash
pip install python-dotenv
```

Adicione ao `settings.py` (no topo):

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env
```

#### 4. Testar Envio de Email

No Django shell:

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    subject='Teste de Email',
    message='Este é um email de teste do Tucupi Labs!',
    from_email='tucupilabs@gmail.com',
    recipient_list=['seu-email-pessoal@gmail.com'],
    fail_silently=False,
)
```

Se tudo estiver correto, você receberá o email em alguns segundos!

---

## 🔧 Troubleshooting

### Erro: "SMTPAuthenticationError: Username and Password not accepted"

**Solução:**
- Verifique se a senha de app está correta (sem espaços)
- Confirme que a verificação em duas etapas está ativada
- Tente gerar uma nova senha de app

### Erro: "SMTPException: STARTTLS extension not supported"

**Solução:**
- Verifique se `EMAIL_USE_TLS=True`
- Porta deve ser `587` (não `465`)

### Erro: "Connection timeout"

**Solução:**
- Verifique sua conexão de internet
- Alguns firewalls/antivírus bloqueiam SMTP
- Tente desabilitar temporariamente para testar

### Email não chega (sem erro)

**Verifique:**
- Pasta de SPAM
- Email está correto em `recipient_list`
- Conta Gmail não está com limite diário atingido (500 emails/dia para contas normais)

---

## 📊 Configurações Recomendadas

### Desenvolvimento
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
✅ Rápido, sem configuração externa

### Staging/Homologação
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=tucupilabs@gmail.com
# Enviar emails reais mas para domínio de teste
```

### Produção
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=tucupilabs@gmail.com
# Considerar serviços profissionais: SendGrid, Mailgun, AWS SES
```

---

## 🚀 Próximos Passos

Com o email configurado, você pode:

1. ✅ Enviar emails de confirmação de candidatura de auditor
2. ✅ Notificar aprovação/rejeição de auditores
3. ✅ Enviar alertas para admins sobre novas candidaturas
4. ✅ Implementar reset de senha por email (futuro)
5. ✅ Notificações de transações (futuro)

---

## 📚 Referências

- [Django Email Documentation](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
