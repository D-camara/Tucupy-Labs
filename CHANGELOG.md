# Changelog

All notable changes to the EcoTrade platform.

## [Unreleased]

### 2025-10-29 - Task 5: Dashboard, Admin e QA Completo ✅
- **Dashboard por papel implementado e testado**
  - Métricas específicas para PRODUCER: carteira, créditos listados, total de vendas
  - Métricas específicas para COMPANY: carteira, créditos disponíveis, total adquirido
  - Visualização das últimas 5 transações do usuário
  - 10 testes cobrindo todas as funcionalidades do dashboard
- **Admin Django completamente configurado**
  - User, Profile, CarbonCredit, CreditListing, Transaction registrados
  - list_display configurado com campos relevantes
  - list_filter e search_fields para facilitar navegação
  - 5 testes verificando registro de todos os models
- **Suite de testes robusta: 42 testes passando**
  - Accounts: 14 testes (autenticação, perfil, RBAC)
  - Credits: 8 testes (marketplace, criação, listagem)
  - Theme/UI: 9 testes (Tailwind, componentes, renderização)
  - Dashboard: 10 testes (métricas, admin, visualizações)
  - Transactions: 1 teste (model)
  - E2E: 1 teste (fluxo parcial: criar → listar)
- **PLAN.md atualizado com status das fases**
- **Documentação completa em PT-BR**

### 2025-10-29 - Tasks 1-3: UI, Auth, Credits ✅
- Implementado Tailwind CSS v4 com tema eco personalizado
- Sistema de autenticação completo (registro, login, logout, perfil)
- Marketplace de créditos com paginação e filtros
- RBAC implementado (Producer/Company mixins e decorators)
- Templates responsivos usando base.html e componentes reutilizáveis

### 2025-10-29 - Dashboard e Testes
- Implementado dashboard com métricas por papel (PRODUCER/COMPANY)
- Adicionadas métricas: carteira, créditos listados, total de vendas/compras
- Implementada visualização de últimas transações
- Configurado admin para todos os models com list_display útil
- Adicionados testes e2e para o fluxo completo de créditos
- Adicionados testes de model para transações

### 2025-10-29 - Tailwind CSS v4 Setup Plan
- Researched django-tailwind v4 compatibility
- Selected django-tailwind-4[reload] package for v4 support
- Created comprehensive TAILWIND_SETUP.md guide
- Defined v4-specific setup: @import, @theme directive, @source paths
- Auto-reload workflow: single `tailwind dev` command
- Browser auto-reload via django-browser-reload
- Custom eco color theme defined (#10b981, #059669, #047857)
- Updated PLAN.md Phase 1 with v4 setup steps
- Tech stack updated: TailwindCSS 4.x, Node.js 18+

### 2025-10-29 - Tailwind v4 Wiring
- Updated AGENTS.md to TailwindCSS 4.x and v4 workflow
- Added `django-tailwind-4[reload]` and `django-browser-reload` to requirements.txt
- Wired `tailwind` and `django_browser_reload` in settings (apps, middleware)
- Added browser reload URL pattern in `ecotrade/urls.py`
 - Scaffolded `theme` app with base template and v4 CSS
 - Updated dashboard template to extend `base.html` and use Tailwind components

### 2025-10-29 - Bootstrap Scaffolding
- Added initial Django project structure (`ecotrade` project, `manage.py`)
- Created apps: `accounts`, `credits`, `transactions`, `dashboard`
- Implemented custom `accounts.User` model with role field
- Added core models for credits and transactions
- Configured settings, URLs, and a minimal dashboard template
- Added `requirements.txt` (Django>=5,<6)

### 2025-10-29 - Project Planning
- Created comprehensive implementation plan for EcoTrade platform
- Defined 4 Django apps: accounts, credits, transactions, dashboard
- Established database models for User, Profile, CarbonCredit, CreditListing, Transaction
- Defined URL structure and template organization
- Tech stack: Django 5.x, Python 3.11+, TailwindCSS 3.x, SQLite (dev)
- Outlined 6 implementation phases
- Architecture: marketplace model with producer credit listings and company purchases
