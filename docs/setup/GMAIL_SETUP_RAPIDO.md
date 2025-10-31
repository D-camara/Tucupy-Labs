# 🚀 Configuração Rápida - Envio de Email com Gmail

## ⚡ Passo a Passo (5 minutos)

### 1️⃣ Ativar Verificação em Duas Etapas no Gmail

1. Acesse: https://myaccount.google.com/security
2. Procure por **"Verificação em duas etapas"**
3. Clique em **"Ativar"** (se ainda não estiver)
4. Siga os passos (geralmente pede número de telefone)
5. ✅ Pronto! A verificação em duas etapas estará ativa

---

### 2️⃣ Gerar Senha de App

1. Ainda em https://myaccount.google.com/security
2. Procure por **"Senhas de app"** (pode estar em "Como fazer login no Google")
3. Clique em **"Senhas de app"**
4. Você verá uma tela para criar senha
5. Preencha:
   - **Selecione o app**: "Outro (nome personalizado)"
   - **Digite**: `Django Tucupi Labs`
6. Clique em **"Gerar"**
7. 🔑 O Google mostrará uma senha de 16 caracteres

**Exemplo:**
```
abcd efgh ijkl mnop
```

8. ⚠️ **COPIE ESSA SENHA** (aparece só uma vez!)
9. Cole **SEM ESPAÇOS**: `abcdefghijklmnop`

---

### 3️⃣ Configurar no Projeto

1. Abra o arquivo `.env` na raiz do projeto
2. Localize a linha:
   ```env
   EMAIL_HOST_PASSWORD=
   ```
3. Cole a senha (sem espaços):
   ```env
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ```
4. Salve o arquivo

---

### 4️⃣ Testar Envio

No terminal (com ambiente virtual ativado):

```bash
python manage.py test_email seu-email@gmail.com
```

**Substitua** `seu-email@gmail.com` pelo seu email pessoal para teste.

Se tudo estiver certo, você verá:
```
✅ Email enviado com sucesso!
📬 Email real enviado para seu-email@gmail.com!
   Verifique sua caixa de entrada (e spam).
```

E receberá um email em alguns segundos! 📧

---

## 🎯 Estado Atual

Após configurar, o sistema funcionará assim:

```
tucupilabs@gmail.com 
        ↓
   [Gmail SMTP]
        ↓
candidato@example.com ✉️
```

**Emails serão enviados de verdade**, mesmo rodando localmente!

---

## ❓ Problemas Comuns

### "Username and Password not accepted"
- ✅ Confirme que verificação em 2 etapas está ATIVA
- ✅ Certifique que usou senha de APP (não a senha normal)
- ✅ Cole a senha SEM espaços no .env
- ✅ Tente gerar uma nova senha de app

### "Connection timeout"
- ✅ Verifique sua internet
- ✅ Firewall/antivírus pode estar bloqueando porta 587
- ✅ Tente desabilitar temporariamente para testar

### Email não chega
- ✅ Verifique pasta de SPAM
- ✅ Email digitado está correto?
- ✅ Gmail tem limite de 500 emails/dia

---

## 🎨 Como Funciona

Quando qualquer parte do código chamar:

```python
from django.core.mail import send_mail

send_mail(
    'Assunto do Email',
    'Conteúdo da mensagem aqui',
    'tucupilabs@gmail.com',          # Remetente
    ['candidato@example.com'],        # Destinatário
    fail_silently=False,
)
```

O Django vai:
1. ✅ Conectar no Gmail via SMTP
2. ✅ Autenticar com a senha de app
3. ✅ Enviar o email de tucupilabs@gmail.com
4. ✅ Destinatário recebe email real na caixa de entrada

---

## 📝 Arquivos Importantes

- `.env` - **Suas credenciais aqui** (não comitar no git!)
- `settings.py` - Configurações de email
- `test_email.py` - Comando para testar envio

---

## ✅ Checklist

- [ ] Verificação em duas etapas ATIVA no Gmail
- [ ] Senha de app GERADA
- [ ] Senha colada no `.env` (sem espaços)
- [ ] `python manage.py test_email seu-email@gmail.com` funcionou
- [ ] Email recebido na caixa de entrada

**Tudo OK? Agora o sistema pode enviar emails reais! 🎉**
