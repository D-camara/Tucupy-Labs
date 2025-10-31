# Changelog

## 2025-10-31

### Added - Icon Usage Guidelines (Lucide over Emojis)
- **AGENTS.md**: Added comprehensive "Icons & Visual Elements" section
  - Explicit rule: Use Lucide icons, NOT emojis in web templates
  - Exception documented: Email templates retain emojis (no JS support)
  - Common emoji → Lucide mappings (14 common patterns)
  - Implementation patterns with code examples
  - Tailwind sizing guide (w-3 through w-8+)
  - Dynamic icon initialization guide
  - Accessibility guidance (ARIA labels)

- **CLAUDE.md**: Added "Icons (Lucide, Not Emojis)" section
  - Quick reference for basic usage
  - Categorized icon mappings (Status, Workflow, Info, Data, Global, Action)
  - Tailwind size reference
  - Email template exception clearly stated
  - Dynamic initialization snippet
  - Links to Lucide docs and PLAN.md

- **Rationale**:
  - Establishes Lucide icons as the standard across the codebase
  - Prevents future emoji usage in web templates
  - Documents migration work completed today
  - Provides clear patterns for new development
  - Ensures consistency in UI/UX going forward

### Changed - Emoji to Lucide Icon Migration
- **Completed migration**: 22 emoji replacements across 6 template files
  - templates/landing.html (8 emojis)
  - templates/api_docs.html (5 emojis)
  - dashboard/templates/dashboard/index.html (4 emojis)
  - transactions/templates/transactions/public_transactions.html (2 emojis)
  - accounts/templates/accounts/add_balance.html (1 emoji)
  - credits/templates/credits/detail.html (1 emoji)

- **Email templates preserved**: templates/emails/*.html retain emojis
  - Email clients don't support JavaScript-based icons
  - Universal emoji support ensures compatibility

- **Documentation**: PLAN.md updated with complete migration reference
  - Full emoji → Lucide mapping table
  - Implementation patterns
  - Benefits and rationale
  - Email template exclusion documented

### Changed - Tailwind Build Output
- `theme/static/css/dist/` removed from git tracking (already in .gitignore)
- Build artifacts now ignored properly

### Fixed - UX e Linguagem Simplificada
- **Logout agora redireciona para landing page** (não mais para tela de login)
  - `accounts/views.py`: `LogoutView.next_page` mudado de `dashboard:index` para `dashboard:landing`
  - Experiência mais natural: usuário sai e volta à página inicial pública

- **Linguagem técnica removida da landing page** (seção API)
  - **Antes**: "GET /api/stats/", "JSON Estruturado", "Endpoints Disponíveis"
  - **Depois**: Linguagem acessível para não-programadores:
    - "📊 Números Gerais" - Quantos créditos existem, quanto CO₂ foi compensado
    - "📋 Lista de Créditos" - Veja todos os créditos aprovados
    - "🔍 Detalhes Completos" - Busque informações específicas
    - "🌐 Acesso Livre" - Qualquer pessoa pode ver
    - "✅ Informação Confiável" - Créditos verificados
    - "⚡ Sempre Atualizado" - Números mais recentes
    - "🔒 Privacidade Protegida" - Dados pessoais não aparecem
  - Botão mudado: "Explorar Documentação Interativa" → "Ver Dados Públicos Agora"
  - Subtítulo: "📱 Clique e veja tudo direto no navegador • Não precisa instalar nada"

### Security - Anonimização de Dados na API Pública
- **Problema Identificado**: API pública expunha informações sensíveis (nomes de usuários, fazendas, notas de auditores)
- **Solução**:
  - **Dados Removidos**:
    - `origin` (nome de fazenda/projeto) - proteção de propriedade privada
    - `owner.username` - substituído por `owner_type` (apenas PRODUCER/COMPANY)
    - `validated_by.username` - substituído por `is_validated` (booleano)
    - `auditor_notes` - pode conter informações confidenciais
  
  - **Dados Mantidos (Anonimizados)**:
    - `id`, `amount`, `unit` - dados quantitativos agregados
    - `generation_date`, `created_at`, `validated_at` - datas públicas
    - `status`, `validation_status` - estados do crédito
    - `owner_type` - tipo do produtor sem identificação
    - `is_validated` - se foi aprovado por auditor (sim/não)
  
  - **Arquivos Atualizados**:
    - `api/views.py`: Serialização anonimizada nos endpoints `/credits/` e `/credits/{id}/`
    - `templates/api_docs.html`: UI atualizada para refletir dados públicos permitidos
    - `api/tests/test_api.py`: Testes verificam anonimização (9/9 passando)
    - `API_DOCS.md`: Documentação atualizada com avisos de privacidade

### Added - API Pública com Documentação Simplificada (Tucupi Labs Branding)

### Fixed - Dashboard do Auditor e Visualização de Créditos do Produtor
- **Problemas Identificados**:
  1. Dashboard do auditor mostrava contagem de "Em Análise" mas não exibia os créditos
  2. Créditos aprovados não apareciam no dashboard do produtor após aprovação

- **Soluções Implementadas**:
  
  **1. Filtro "Em Análise" no Dashboard do Auditor** (`credits/views.py` - `auditor_dashboard`):
  - Adicionado filtro `validated_by=request.user` na aba "under_review"
  - Agora mostra apenas créditos em análise pelo auditor atual
  - Contagem (`under_review_count`) também filtra por auditor atual
  - Evita confusão: auditor vê apenas créditos que ele iniciou análise
  
  **2. Lista de Créditos no Dashboard do Produtor** (`dashboard/views.py` e `dashboard/templates/dashboard/index.html`):
  - Adicionado filtro `is_deleted=False` em `my_credits` (carteira)
  - Adicionado contexto `producer_credits` com todos os créditos não deletados do produtor
  - Criada seção visual "Meus Créditos" no dashboard com grid de cards
  - Cards mostram:
    - Badge colorido do status de validação (APPROVED/PENDING/UNDER_REVIEW/REJECTED)
    - Informações do crédito (amount, origin, status)
    - Nome do auditor que validou (se aplicável)
    - Data de criação
    - Link direto para página de detalhes
  - Botão "Criar Crédito" no topo da seção
  
  **3. Estrutura Visual dos Cards de Crédito**:
  - APPROVED: Badge verde com ✅
  - PENDING: Badge amarelo com 🟡 e animação pulse
  - UNDER_REVIEW: Badge azul com 🔵 e animação pulse
  - REJECTED: Badge vermelho com ❌
  - Design responsivo com grid (1 coluna mobile, 2 tablet, 3 desktop)
  - Efeito hover com glow e transição suave

### Added - Validação de Créditos por Auditores Antes do Marketplace
- **Requisito**: Créditos devem ser aprovados por auditores antes de aparecerem no marketplace
- **Implementação**:
  - **Marketplace Filtering** (`credits/views.py` - `MarketplaceListView`):
    - Adicionado filtro `credit__validation_status=CarbonCredit.ValidationStatus.APPROVED`
    - Apenas créditos aprovados aparecem no marketplace público
  
  - **List-for-Sale Validation** (`credits/views.py` - `list_for_sale`):
    - Validação antes de criar listing: verifica se `validation_status == APPROVED`
    - Mensagem de erro: "Este crédito precisa ser aprovado por um auditor antes de ser listado."
    - Previne listagem manual de créditos não aprovados
  
  - **Validation Status Display** (`credits/templates/credits/detail.html`):
    - Card "Status de Validação" com badges coloridos:
      - APPROVED: Verde (✅)
      - PENDING: Amarelo com animação pulse (🟡)
      - UNDER_REVIEW: Azul com animação pulse (🔵)
      - REJECTED: Vermelho (❌)
    - Exibe nome do auditor que validou (`validated_by.username`)
    - Formatação de data/hora da validação
  
  - **Success Message** (`credits/views.py` - `CreditCreateView`):
    - Mensagem ao criar crédito: "Crédito criado com sucesso! Ele será revisado por um auditor antes de poder ser listado no marketplace."
    - Import de `django.contrib.messages` adicionado

- **Workflow Completo**:
  1. Producer cria crédito → `validation_status = PENDING`
  2. Crédito **NÃO** aparece no marketplace
  3. Producer **NÃO** consegue listá-lo para venda
  4. Auditor revisa e aprova
  5. Crédito pode ser listado e aparece no marketplace

### Fixed - URL Namespaces para Credits e Transactions
- **Problema Identificado**:
  - Apps `credits` e `transactions` não tinham `app_name` definido em seus `urls.py`
  - Causava erro `NoReverseMatch: 'credits' is not a registered namespace` ao fazer login
  - Dashboard e templates não conseguiam resolver URLs como `credits:auditor_dashboard`

- **Solução**:
  - Adicionado `app_name = "credits"` em `credits/urls.py`
  - Adicionado `app_name = "transactions"` em `transactions/urls.py`
  - Atualizado 7 templates para usar namespaces corretos:
    - `templates/components/navbar.html`
    - `transactions/templates/transactions/*.html`
    - `credits/templates/credits/*.html`
  - Atualizado testes em `credits/tests/test_views.py`
  - Script `update_urls.py` criado para automação

### Fixed - Layout do Admin Dashboard (Botões de Aprovação)
- **Problema Identificado**:
  - Botões "Aprovar" e "Rejeitar" não apareciam nas candidaturas pendentes
  - Justificativa do candidato saía da tela sem quebra de linha
  - Estrutura flex com `flex-1` ocupava todo o espaço disponível

- **Solução**:
  - Refatorado layout do card de candidatura
  - Botões movidos para rodapé com `flex justify-between`
  - Justificativa com `break-words` e `whitespace-pre-wrap`
  - Layout responsivo e organizado em seções claras

### Fixed - Candidatura de Auditor com created_at NULL
- **Problema Identificado**:
  - Candidatura ID 1 (user: teste) tinha `created_at = None`
  - Foi criada antes da migration que adicionou o campo `created_at`
  - Causava erro `IntegrityError: NOT NULL constraint failed` ao tentar aprovar

- **Solução**:
  - Removida candidatura problemática do banco de dados
  - Novas candidaturas sempre terão `created_at` válido (auto_now_add=True)
  - Management commands criados para diagnóstico:
    - `check_applications`: verifica status das candidaturas
    - `show_raw_data`: mostra dados brutos da tabela

### Fixed - Acesso de Superusers ao Dashboard Admin
- **Propriedade is_admin** (`accounts/models.py`):
  - Adicionada propriedade `User.is_admin` que retorna `True` para superusers ou usuários com role ADMIN
  - Permite que superusers acessem dashboard administrativo sem precisar de role específica

- **Signal de Auto-Promoção**:
  - Signal `create_or_update_user_profile` agora detecta quando um usuário é superuser
  - Automaticamente atribui `role=ADMIN` para todos os superusers (novo e existente)
  - Garante que superusers sempre tenham permissões administrativas

- **Management Command** (`update_superuser_roles`):
  - Comando criado para atualizar role de superusers existentes
  - Execução: `python manage.py update_superuser_roles`
  - Promoveu 3 superusers para role ADMIN

- **Atualização de Views**:
  - `admin_dashboard_view`: mudou de `user.role != User.Roles.ADMIN` para `not user.is_admin`
  - `approve_auditor_view`: mudou para verificação com `not user.is_admin`
  - `reject_auditor_view`: mudou para verificação com `not user.is_admin`
  - Agora superusers têm acesso completo ao dashboard admin

- **Atualização de Templates**:
  - `navbar.html`: mudou de `{% if user.role == 'ADMIN' %}` para `{% if user.is_admin %}`
  - Link "Admin" agora aparece para superusers e usuários com role ADMIN
  - Atualizado tanto na versão desktop quanto mobile do menu

### Added - Sistema de Validação de Créditos por Auditores
- **Modelo de Candidatura de Auditor** (`AuditorApplication`):
  - 13 campos: dados pessoais, documentos (certificado, currículo), motivação, termos
  - Status: PENDING, APPROVED, REJECTED
  - Métodos: `approve()`, `reject()` com envio automático de emails
  - Upload de arquivos com validações (tamanho máximo 5MB, formatos permitidos)

- **Campos de Validação em CarbonCredit**:
  - `validation_status`: PENDING, UNDER_REVIEW, APPROVED, REJECTED
  - `validated_by`: FK para User (auditor)
  - `validated_at`: timestamp da validação
  - `auditor_notes`: observações do auditor
  - Métodos: `approve_validation()`, `reject_validation()`, `start_review()`
  - Propriedades: `can_be_listed`, `is_pending_validation`, `is_approved`

- **Formulário de Candidatura** (`accounts/forms.py`):
  - Validação de certificado: 5MB max, PDF/JPG/PNG
  - Validação de currículo: 5MB max, PDF
  - Validação de LinkedIn: URL deve conter "linkedin.com"
  - Auto-preenchimento com dados do usuário logado
  - Termos de aceite obrigatórios

- **Sistema de Emails** (7 notificações):
  - Confirmação de candidatura (usuário)
  - Aprovação de candidatura (usuário)
  - Rejeição de candidatura com motivo (usuário)
  - Nova candidatura para revisão (admins)
  - Solicitação de validação de crédito (auditor)
  - Crédito aprovado (produtor)
  - Crédito rejeitado com observações (produtor)
  - Templates HTML profissionais com gradient verde/azul

- **Ações no Admin**:
  - Aprovação em lote de candidaturas (promove para AUDITOR, envia email)
  - Rejeição em lote de candidaturas (com motivo padrão, envia email)
  - Badges coloridos para status (amarelo/verde/vermelho)
  - Fieldsets organizados para melhor UX

- **Seção de Auditores na Landing Page**:
  - Bloco dedicado "Torne-se Auditor" antes do CTA final
  - Design com gradient azul/roxo para diferenciar
  - 4 cards de benefícios: validação, renda, networking, certificação
  - CTAs condicionais baseados em autenticação e role
  - Exibição de estatísticas: número de auditores, créditos validados
  - Seção de requisitos com 4 cards informativos

- **Dashboard de Auditoria** (`credits/views.py`, template):
  - 3 abas: Pendentes, Em Análise, Histórico
  - 4 cards de estatísticas: pending, under_review, approved_by_me, rejected_by_me
  - Lista de créditos com informações detalhadas
  - Badges coloridos para status de validação
  - Botões de ação contextuais (Revisar/Continuar Análise)
  - Estado vazio diferenciado por aba
  - Acesso restrito a role AUDITOR

- **Interface de Revisão de Crédito** (`review_credit.html`):
  - Exibição completa dos dados do crédito
  - Informações do proprietário (produtor)
  - Histórico de observações anteriores (se houver)
  - Formulário com textarea para notas do auditor
  - 3 botões de ação: Iniciar Análise, Aprovar, Rejeitar
  - Confirmação JavaScript para rejeição
  - Diretrizes de validação inline
  - Bloqueio após validação (read-only)

- **Interface de Visualização** (`view_credit.html`):
  - Cards de status (validação + listagem)
  - Informações detalhadas do crédito
  - Histórico de validação com timeline
  - Observações do auditor (se houver)
  - Estado visual para créditos aguardando validação
  - Informações educacionais sobre créditos de carbono

- **Navegação Atualizada**:
  - Link "Auditoria" no navbar para usuários com role AUDITOR (desktop + mobile)
  - Ícone de escudo para identificação visual
  - Hover azul para diferenciar de outras seções

### Changed
- Role `AUDITOR` adicionado ao modelo `User` com propriedade `is_auditor`
- Configuração de MEDIA_URL e MEDIA_ROOT para upload de arquivos
- URLs de desenvolvimento servem arquivos de media
- Landing page agora exibe estatísticas de auditores

### Technical Details
- Branch: `Validação-de-créditos`
- Novas URLs:
  - `/accounts/auditor/apply/` - Formulário de candidatura
  - `/credits/audit/dashboard/` - Dashboard de auditoria
  - `/credits/audit/<id>/review/` - Interface de revisão
  - `/credits/audit/<id>/view/` - Visualização de crédito
- Emails via SMTP Gmail (tucupilabs@gmail.com)
- Permissões: `@login_required` para candidatura, role check para dashboard
- Notificações: Emails enviados assincronamente (try/except não bloqueia fluxo)

### UX Improvements
- **Fluxo de Candidatura Simplificado**:
  - Criado formulário único (`AuditorRegistrationForm`) que combina registro de usuário + candidatura
  - Auditores têm fluxo de cadastro separado de Produtores/Empresas
  - Link direto na landing page vai para o formulário específico de auditores
  - Após preencher formulário: usuário criado automaticamente, login feito, candidatura enviada
  - Dois botões na landing para não autenticados: "Candidatar-se Agora" (auditor) e "Criar Conta Produtor/Empresa" (normal)

- **Dashboard Administrativo Moderno** (`/accounts/admin/dashboard/`):
  - Interface visual profissional com gradiente roxo/rosa
  - 4 cards de estatísticas: usuários (por role), candidaturas, créditos, transações
  - 3 abas principais:
    - **Candidaturas Pendentes**: Lista completa com todos os dados, links para documentos, botões de aprovar/rejeitar
    - **Histórico**: Tabela com todas as candidaturas (aprovadas/rejeitadas) e quem revisou
    - **Usuários Recentes**: Últimos 10 usuários registrados com tipo e status
  - Aprovação com 1 clique (com confirmação)
  - Rejeição com formulário para escrever motivo personalizado
  - Sistema de tabs com JavaScript para navegação fluida
  - Badges coloridos para status (amarelo/verde/vermelho)
  - Links para download de certificados e currículos
  - Acesso restrito: apenas role ADMIN
  - Link "Admin" no navbar (desktop + mobile) para administradores

## 2025-10-30

### Added
- **Landing Page**: Página inicial pública moderna e atraente
  - Hero section com animações e estatísticas em tempo real
  - Seção de features destacando 6 principais diferenciais (verificação transparente, tempo real, impacto regional, etc.)
  - Seção "Como Funciona" com 3 passos simples (Cadastro → Marketplace → Transação)
  - Cards diferenciados para Produtores e Empresas com benefícios específicos
  - CTA final com múltiplos pontos de conversão
  - Totalmente responsivo com animações suaves
  - Integração com estatísticas reais do banco de dados
  - Ícones Lucide SVG para melhor consistência visual
  - URL: `/` (raiz do site) - view pública sem necessidade de login
  - Dashboard movido para `/dashboard/` (apenas usuários autenticados)

- **Public Real-Time Transactions Page**: Live transparency feed for marketplace activity
  - New public page (`/transactions/public/`) - no auth required
  - Server-Sent Events (SSE) for real-time updates
  - Shows last 10 COMPLETED transactions with auto-refresh
  - Anonymized data: only participant roles (Company/Producer), no personal info
  - **Session-based reconnection system**:
    - Unique session ID generated per connection, stored in localStorage
    - Reconnections within 60s bypass rate limit (allows page refresh)
    - Session auto-refreshed every 10s while active
    - Auto-cleanup when user leaves (not just refresh)
  - Smart rate limiting: 5s initial timeout, auto-refreshes to 30s while connected
  - Immediate connection confirmation (fast "Live" status update)
  - Connection status indicator with auto-reconnect (3s cooldown)
  - Relative timestamps ("2 mins ago")
  - Main nav link added for visibility
  - Features: live updates, privacy protection, full transparency, seamless reconnection

## 2025-10-30

### Changed
- **Tailwind v4 Theme Migration**: Migrated theme config from JS to CSS for v4 compatibility
  - Moved all theme extensions from `tailwind.config.js` to `styles.css` using `@theme` directive
  - Converted colors (Tucupi brand palette), fonts, animations, shadows to CSS variables
  - Added custom keyframes (`fadeIn`, `slideUp`, `slideDown`, `scaleIn`, `glow`) as standard CSS
  - Custom background utilities (`bg-gradient-radial`, `bg-gradient-conic`, `bg-grid-pattern`) in `@layer utilities`
  - Retained legacy `eco-*` color aliases for backward compatibility
- **Icon Migration**: Replaced all emojis (19 unique) with Lucide SVG icons
  - Migrated 12 template files across all apps
  - Added Lucide CDN to `base.html` with auto-initialization
  - Icon mappings: 🌱→sprout, 💵→banknote, 🏢→building-2, 📊→bar-chart-3, ✓→check, 🔗→link, 🌍→globe, 📜→scroll-text, 🔒→lock, 💰→wallet, 🛒→shopping-cart, 📦→package, 🟢→circle (filled), 🌾→wheat, 👤→user, 📥→download, 📤→upload, ⏳→clock, ✗→x
  - Benefits: better consistency, accessibility, customizability
- **Template Reorganization**: Moved app-specific templates to respective app directories
  - All apps now follow Django best practice: `app/templates/app/` structure
  - `accounts`: Moved login, register, profile, add_balance to `accounts/templates/accounts/`
  - `credits`: Moved 5 templates (marketplace, create, detail, etc.) to `credits/templates/credits/`
  - `dashboard`: Moved index to `dashboard/templates/dashboard/`
  - `transactions`: Moved history to `transactions/templates/transactions/`
  - Root `templates/` now contains shared templates: `base.html` and `components/` folder
  - Moved `base.html` from `theme/templates/` to root `templates/` (shared base template)
  - Updated all view references to use app-prefixed paths (e.g., "accounts/login.html")

### Added
- **Blockchain-style Ownership History**: Immutable audit trail for carbon credits
  - New `CreditOwnershipHistory` model tracking all ownership transfers
  - Automatic tracking via Django signals (post_save on CarbonCredit)
  - Public history view (`/credits/<id>/history/`) - full transparency
  - Timeline UI showing complete transfer chain (GENESIS → current owner)
  - Transfer types: CREATION (initial), SALE (marketplace purchase), TRANSFER (manual)
  - Links to related transactions with price data
  - Soft delete on CarbonCredit (is_deleted flag) - prevents data loss
  - Custom managers: `objects` (filters deleted), `objects_all` (includes all)
  - Legacy credit support: auto-creates GENESIS entries for existing credits
- **Seed Commands Enhanced**:
  - `seed_credits`: Reports GENESIS history entries created via signals
  - `seed_transactions`: Reports SALE history entries created via signals
  - `seed_ownership_transfers`: NEW - Creates multi-hop transfer chains for demo
  - `show_ownership_stats`: NEW - Displays ownership history statistics
