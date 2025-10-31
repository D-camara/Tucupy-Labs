# Plano de Testes - Sistema de Validação de Auditores

Este documento descreve o plano de testes end-to-end para o sistema de validação de créditos por auditores.

## Pré-requisitos

1. Servidor Django rodando: `python manage.py runserver`
2. Tailwind rodando: `python manage.py tailwind dev`
3. Banco de dados migrado: `python manage.py migrate`
4. Pelo menos um usuário ADMIN criado: `python manage.py createsuperuser`

## Fluxo de Teste Completo

### 1. Candidatura de Auditor

**Objetivo**: Testar o processo de candidatura como auditor

**Passos**:
1. Criar um novo usuário PRODUCER:
   - Acessar `/accounts/register/`
   - Preencher formulário escolhendo role "Produtor"
   - Confirmar registro e fazer login

2. Acessar a landing page (`/`):
   - Verificar se a seção "Torne-se Auditor" está visível
   - Verificar estatísticas (número de auditores e créditos validados)
   - Clicar em "Candidate-se Agora"

3. Preencher formulário de candidatura (`/accounts/auditor/apply/`):
   - **Dados Pessoais**:
     - Nome completo (deve vir pré-preenchido)
     - Email (deve vir pré-preenchido)
     - Telefone: (91) 98765-4321
     - Organização: Consultoria Ambiental XYZ
     - LinkedIn: https://linkedin.com/in/seuusuario
   
   - **Documentos**:
     - Certificado: Fazer upload de PDF (max 5MB)
     - Currículo: Fazer upload de PDF (max 5MB)
   
   - **Motivação**:
     - Justificativa: "Tenho 10 anos de experiência em auditoria ambiental..."
   
   - **Termos**:
     - Marcar checkbox de aceite
   
   - Clicar em "Enviar Candidatura"

4. Verificar mensagem de sucesso
5. Verificar email de confirmação (tucupilabs@gmail.com)

**Resultado Esperado**:
- ✅ Formulário validado corretamente
- ✅ Candidatura salva no banco com status PENDING
- ✅ Email de confirmação enviado ao candidato
- ✅ Email de notificação enviado aos admins
- ✅ Redirect para página de perfil com mensagem de sucesso

**Validações a Testar**:
- ❌ Tentar enviar sem marcar termos → erro
- ❌ Tentar enviar arquivo > 5MB → erro
- ❌ Tentar enviar imagem como currículo → erro (só PDF)
- ❌ Tentar LinkedIn sem "linkedin.com" → erro
- ❌ Tentar candidatar-se novamente (já tem pending) → bloqueio
- ❌ Usuário já AUDITOR tentar candidatar-se → bloqueio

---

### 2. Aprovação pelo Admin

**Objetivo**: Aprovar candidatura e promover usuário a AUDITOR

**Passos**:
1. Acessar Django Admin (`/admin/`)
2. Login como superuser
3. Navegar para "Accounts" → "Candidaturas de Auditor"
4. Ver a candidatura pendente (badge amarelo "PENDENTE")
5. Selecionar candidatura
6. No dropdown de ações, escolher "✅ Aprovar candidaturas selecionadas"
7. Clicar em "Ir"
8. Confirmar ação

**Resultado Esperado**:
- ✅ Status muda para APPROVED (badge verde)
- ✅ Campo `reviewed_by` preenchido com admin que aprovou
- ✅ Campo `reviewed_at` com timestamp
- ✅ User.role muda de PRODUCER para AUDITOR
- ✅ Email de aprovação enviado ao candidato
- ✅ Mensagem de sucesso no admin: "1 candidatura(s) aprovada(s)"

**Verificações**:
- Fazer logout do admin
- Fazer login com o usuário aprovado
- Verificar que `user.is_auditor` é True
- Verificar que link "Auditoria" aparece no navbar

---

### 3. Acesso ao Dashboard de Auditoria

**Objetivo**: Verificar interface do dashboard de auditores

**Passos**:
1. Logado como AUDITOR, clicar em "Auditoria" no navbar
2. Deve abrir `/credits/audit/dashboard/`
3. Verificar layout:
   - 4 cards de estatísticas no topo
   - 3 abas: Pendentes, Em Análise, Histórico
   - Lista de créditos (pode estar vazia inicialmente)

**Resultado Esperado**:
- ✅ Dashboard carrega sem erros
- ✅ Estatísticas mostram zeros (se não houver créditos)
- ✅ Abas funcionam (JavaScript)
- ✅ Estado vazio mostra mensagens adequadas

**Teste de Permissão**:
- Fazer logout
- Fazer login como PRODUCER (não auditor)
- Tentar acessar `/credits/audit/dashboard/`
- ❌ Deve retornar 403 Forbidden ou redirect

---

### 4. Criação de Crédito para Validar

**Objetivo**: Criar crédito que precisa ser validado

**Passos**:
1. Fazer logout
2. Criar novo usuário PRODUCER (ou usar existente)
3. Fazer login como PRODUCER
4. Acessar dashboard → "Meus Créditos" → "Criar Novo Crédito"
5. Preencher formulário:
   - Quantidade: 100
   - Unidade: tCO2e
   - Origem: Projeto de Reflorestamento ABC
   - Data de Geração: (data passada, ex: 01/01/2024)
6. Salvar crédito

**Resultado Esperado**:
- ✅ Crédito criado com `validation_status = PENDING`
- ✅ `is_verified = False`
- ✅ Campo `validated_by` vazio
- ✅ Crédito NÃO aparece em marketplace (can_be_listed = False)

**Verificações**:
- Acessar `/credits/marketplace/`
- Verificar que o crédito não está listado
- Acessar perfil do produtor
- Verificar que crédito aparece em "Meus Créditos" com badge "Aguardando Validação"

---

### 5. Iniciar Análise de Crédito

**Objetivo**: Auditor inicia revisão de crédito pendente

**Passos**:
1. Fazer login como AUDITOR
2. Acessar Dashboard de Auditoria
3. Na aba "Pendentes", deve aparecer o crédito criado
4. Clicar em "Revisar Crédito"
5. Deve abrir página `/credits/audit/<id>/review/`
6. Verificar informações do crédito:
   - Status: PENDING (badge amarelo)
   - Dados do proprietário
   - Quantidade, origem, data
7. No formulário de validação:
   - Campo "Observações" vazio
   - 3 botões: Iniciar Análise, Aprovar, Rejeitar
8. Preencher campo de observações: "Iniciando análise do projeto..."
9. Clicar em "Iniciar Análise"

**Resultado Esperado**:
- ✅ `validation_status` muda para UNDER_REVIEW
- ✅ `validated_by` = auditor atual
- ✅ Redirect de volta ao dashboard com mensagem de sucesso
- ✅ Crédito agora aparece na aba "Em Análise"
- ✅ Crédito NÃO aparece mais na aba "Pendentes"

---

### 6. Aprovar Crédito

**Objetivo**: Auditor aprova crédito após análise

**Passos**:
1. Na aba "Em Análise", clicar em "Continuar Análise" no crédito
2. Deve abrir `/credits/audit/<id>/review/`
3. Verificar status: UNDER_REVIEW (badge azul)
4. Ver observações anteriores preservadas
5. Editar campo de observações:
   ```
   Análise completa. Documentação adequada.
   Projeto validado conforme normas ISO 14064.
   Quantidade e origem verificadas.
   Aprovado para listagem no marketplace.
   ```
6. Clicar em "Aprovar Crédito"

**Resultado Esperado**:
- ✅ `validation_status` muda para APPROVED
- ✅ `is_verified` muda para True
- ✅ `validated_at` preenchido com timestamp atual
- ✅ `auditor_notes` salva observações completas
- ✅ Email enviado ao produtor notificando aprovação
- ✅ Redirect ao dashboard com mensagem "Crédito aprovado!"
- ✅ Crédito move para aba "Histórico"
- ✅ Card "Aprovados por Mim" incrementa +1

**Verificações**:
- Fazer login como PRODUCER (dono do crédito)
- Verificar email de aprovação recebido
- Acessar "Meus Créditos"
- Verificar badge verde "APROVADO"
- Tentar listar crédito no marketplace → deve funcionar
- Verificar que `can_be_listed = True`

---

### 7. Rejeitar Crédito

**Objetivo**: Auditor rejeita crédito com observações

**Passos**:
1. Criar outro crédito como PRODUCER
2. Login como AUDITOR
3. Acessar Dashboard → aba "Pendentes"
4. Clicar em "Revisar Crédito" no novo crédito
5. Preencher observações:
   ```
   Documentação insuficiente.
   Origem não foi adequadamente comprovada.
   Data de geração inconsistente com registros.
   Por favor, forneça documentação adicional.
   ```
6. Clicar em "Rejeitar Crédito"
7. Confirmar no alert JavaScript

**Resultado Esperado**:
- ✅ `validation_status` muda para REJECTED
- ✅ `is_verified` permanece False
- ✅ `validated_at` e `validated_by` preenchidos
- ✅ Email enviado ao produtor com motivo da rejeição
- ✅ Redirect ao dashboard
- ✅ Crédito move para aba "Histórico"
- ✅ Card "Rejeitados por Mim" incrementa +1

**Verificações**:
- Login como PRODUCER
- Verificar email de rejeição com observações
- Verificar crédito com badge vermelho "REJEITADO"
- Tentar listar no marketplace → deve ser bloqueado
- Verificar que `can_be_listed = False`

---

### 8. Visualização de Crédito (Read-Only)

**Objetivo**: Qualquer usuário pode ver detalhes de um crédito

**Passos**:
1. Login como qualquer usuário autenticado
2. Acessar diretamente `/credits/audit/<id>/view/`
3. Verificar layout:
   - Cards de status (validação + listagem)
   - Informações do crédito
   - Histórico de validação (se já validado)
   - Observações do auditor

**Resultado Esperado**:
- ✅ Página carrega sem erros
- ✅ Informações exibidas corretamente
- ✅ Não há formulários (read-only)
- ✅ Badges coloridos corretos
- ✅ Histórico mostra auditor e timestamp

---

### 9. Workflow Completo End-to-End

**Objetivo**: Testar fluxo completo desde candidatura até compra

**Cenário**:
1. ✅ Usuário A (PRODUCER) se candidata como auditor
2. ✅ Admin aprova → vira AUDITOR
3. ✅ Usuário B (PRODUCER) cria crédito
4. ✅ Usuário A (AUDITOR) aprova crédito
5. ✅ Usuário B lista crédito no marketplace
6. ✅ Usuário C (COMPANY) compra crédito
7. ✅ Transação completa com sucesso

**Verificações Finais**:
- Estatísticas na landing page atualizadas
- Créditos validados aparecem no marketplace
- Dashboard de auditoria mostra estatísticas corretas
- Emails enviados em cada etapa
- Transações funcionam normalmente

---

## Testes de Edge Cases

### Permissões
- ❌ PRODUCER não pode acessar `/credits/audit/dashboard/`
- ❌ COMPANY não pode acessar `/credits/audit/dashboard/`
- ❌ ADMIN não pode acessar (a menos que também seja AUDITOR)
- ❌ Usuário não autenticado deve redirecionar para login

### Validações de Formulário
- ❌ Arquivo > 5MB → erro
- ❌ Formato inválido de arquivo → erro
- ❌ Campo obrigatório vazio → erro
- ❌ LinkedIn sem URL válida → erro
- ❌ Tentar aprovar sem observações → erro

### Estados Inválidos
- ❌ Tentar revisar crédito já APPROVED → bloqueado
- ❌ Tentar revisar crédito já REJECTED → bloqueado
- ❌ Tentar revisar crédito em análise por outro auditor → permitido (mas mostra warning)

### Concorrência
- ⚠️ Dois auditores revisando mesmo crédito → último write vence
- ⚠️ Produtor tenta deletar crédito em análise → deve bloquear

---

## Comandos Úteis para Testes

```bash
# Criar superuser
python manage.py createsuperuser

# Popular banco com dados de teste
python manage.py seed_users
python manage.py seed_credits
python manage.py seed_listings

# Verificar emails no console (se DEBUG_EMAIL=True)
# Olhar terminal onde servidor está rodando

# Resetar banco (CUIDADO: apaga tudo!)
python manage.py flush --noinput
python manage.py migrate
python manage.py createsuperuser

# Acessar shell do Django para queries
python manage.py shell
>>> from accounts.models import User, AuditorApplication
>>> from credits.models import CarbonCredit
>>> AuditorApplication.objects.all()
>>> CarbonCredit.objects.filter(validation_status='PENDING')
```

---

## Checklist de Testes

### Candidatura
- [ ] Formulário carrega corretamente
- [ ] Validações de arquivo funcionam
- [ ] Upload de arquivos funciona
- [ ] Email de confirmação enviado
- [ ] Email para admins enviado
- [ ] Não permite candidatura duplicada
- [ ] Bloqueia AUDITOR/ADMIN de candidatar-se

### Admin
- [ ] Lista de candidaturas visível
- [ ] Badges de status corretos
- [ ] Ação de aprovação funciona
- [ ] Ação de rejeição funciona
- [ ] Emails enviados em aprovação
- [ ] Role do usuário atualizado

### Dashboard
- [ ] Carrega corretamente para AUDITOR
- [ ] Bloqueia não-auditores
- [ ] Estatísticas calculadas corretamente
- [ ] Abas funcionam
- [ ] Filtros de status corretos
- [ ] Estados vazios mostram mensagens

### Revisão
- [ ] Informações do crédito exibidas
- [ ] Botão "Iniciar Análise" funciona
- [ ] Botão "Aprovar" funciona
- [ ] Botão "Rejeitar" funciona
- [ ] Observações salvas corretamente
- [ ] Timestamps registrados
- [ ] Emails enviados ao produtor

### Integração
- [ ] Crédito aprovado pode ser listado
- [ ] Crédito rejeitado não pode ser listado
- [ ] Marketplace filtra corretamente
- [ ] Estatísticas na landing page corretas
- [ ] Navbar mostra link para auditores

---

## Problemas Conhecidos e Soluções

### Problema: Emails não estão sendo enviados
**Solução**: Verificar settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tucupilabs@gmail.com'
EMAIL_HOST_PASSWORD = 'zqmevtjqbedafgue'  # App password
```

### Problema: Arquivos não fazem upload
**Solução**: Verificar:
1. `MEDIA_URL` e `MEDIA_ROOT` em settings.py
2. URLs incluem `static(settings.MEDIA_URL, ...)` em DEBUG
3. Pasta `media/` tem permissões de escrita

### Problema: 403 Forbidden ao acessar dashboard
**Solução**: Verificar que usuário tem `role='AUDITOR'`
```python
# No shell
from accounts.models import User
user = User.objects.get(username='seuusuario')
print(user.role)  # Deve ser 'AUDITOR'
print(user.is_auditor)  # Deve ser True
```

### Problema: Crédito aprovado não aparece no marketplace
**Solução**: Verificar:
1. `validation_status == 'APPROVED'`
2. `is_verified == True`
3. Produtor criou uma `CreditListing` para o crédito
4. `CreditListing.status == 'ACTIVE'`

---

## Relatório de Bugs

Use este template para reportar problemas encontrados durante testes:

```markdown
### Bug: [Título do Bug]

**Descrição**: O que aconteceu?

**Passos para Reproduzir**:
1. 
2. 
3. 

**Resultado Esperado**: O que deveria acontecer?

**Resultado Obtido**: O que aconteceu de fato?

**Screenshots**: (se aplicável)

**Ambiente**:
- Django version: 5.2.7
- Python version: 3.11+
- Browser: Chrome/Firefox/etc
- OS: Windows/Linux/Mac
```

---

## Conclusão

Este plano cobre o fluxo completo do sistema de validação de auditores. Siga os passos em ordem para garantir que todas as funcionalidades estão operacionais.

**Próximos Passos Após Testes**:
1. Corrigir bugs encontrados
2. Adicionar testes automatizados (`tests.py`)
3. Melhorar UX com base em feedback
4. Considerar notificações in-app (além de email)
5. Dashboard de analytics para admins
