# Changelog

All notable changes to the EcoTrade platform.

## [Unreleased]

### 2025-10-29 - UX Improvements: Login/Logout Enhancements 🔐
**Melhorias na experiência de autenticação com validação em tempo real e mensagens personalizadas**

#### Login
- **CustomLoginForm:** Formulário personalizado com validação customizada
- **Styled inputs:** Dark theme (bg-white/5, border-white/10, focus:border-tucupi-green-500)
- **Enhanced error display:** Ícone SVG, estrutura clara, mensagem em português
- **Field icons:** Ícones SVG para username (user) e password (lock)
- **"Esqueceu senha?":** Link para recuperação de senha
- **"Manter conectado":** Checkbox remember me
- **Submit button:** Texto "Entrar na minha conta" com seta animada
- **Divider:** Linha com texto "ou" centralizado
- **"Criar conta" button:** Full-width glass button com ícone SVG

#### Registro
- **Real-time password validation:**
  - JavaScript que valida match de senhas em tempo real
  - Border vermelha + mensagem de erro quando não coincidem
- **Password strength indicator:**
  - 4 barras visuais (red/yellow/blue/green)
  - Texto de força: Fraca/Média/Boa/Forte
  - Critérios: comprimento, maiúsculas/minúsculas, números, caracteres especiais

#### Logout
- **Fixed 405 Method Not Allowed:** Adicionado suporte a GET requests
- **http_method_names:** ['get', 'post', 'options']
- **dispatch() method:** Adiciona success message "👋 Até logo, {username}!"
- **get() method:** Chama post() para manter lógica de logout

#### Messages & Feedback
- **Login error:** "Nome de usuário ou senha incorretos. Verifique e tente novamente."
- **Registration success:** "🎉 Conta criada com sucesso! Bem-vindo, {username} ({role_name})!"
- **Logout success:** "👋 Até logo, {username}!"

#### Bug Fixes
- **dashboard/urls.py:** Adicionado `app_name = "dashboard"` para namespace
- **LogoutView:** Redirect para `reverse_lazy("dashboard:index")` agora funciona
- **register.html:** Fechado bloco `{% endblock %}` antes de `{% block extra_scripts %}`

#### Tests Updated
- **test_login_with_invalid_credentials:** Atualizado para procurar mensagem em português
- **theme/tests/test_ui.py:** Atualizados 8 testes para refletir rebrand Tucupi Labs
  - `dashboard_index` → `dashboard:index`
  - `EcoTrade` → `Tucupi Labs`
  - Classes CSS atualizadas (glass, tucupi-green)
  - Template tags ao invés de URLs hardcoded

**Result:** 47 testes passando ✅

### 2025-10-29 - Redesign Completo: Tucupi Labs Brand Identity 🎨
**Front-end completamente renovado com paleta verde + preto e efeitos modernos**

#### Visual Identity
- **Nome oficial:** Tucupi Labs (substituindo EcoTrade)
- **Paleta de cores:** Verde (#10B981 → #00FF88) + Preto (#0A0A0A)
- **Tipografia:** Inter (corpo) + Space Grotesk (display)
- **Logo:** 🌱 com efeito glow verde neon

#### Design System
- **Glass Morphism:** Cards com backdrop-filter e bordas translúcidas
- **Grid Background:** Padrão de grade sutil com opacidade verde
- **Gradientes:** Verde para verde neon em CTAs e títulos
- **Animações:** fade-in, slide-up, scale-in, pulse-slow, glow
- **Hover Effects:** Transform translateY + box-shadow glow
- **Scrollbar customizada:** Verde sobre preto

#### Componentes Atualizados
- **Navbar:** Sticky com glass effect, mobile menu, ícones SVG, logo animado
- **Footer:** 3 colunas (About, Links, Contato) com gradiente e links
- **Messages:** Glass cards com border-left colorido por tipo
- **Buttons:** Gradiente verde com efeito hover glow e scale
- **Forms:** Inputs dark com focus ring verde, labels em gray-300
- **Cards:** Glass com hover-glow, badges de status coloridos

#### Páginas Redesenhadas
1. **Dashboard (Landing):**
   - Hero com logo animado 8xl e texto gradiente
   - 3 feature cards (Produtor, Empresa, Transparência) com glass effect
   - CTAs com gradiente e shadow-glow-green
   - Dashboard autenticado: cards com ícones, gradientes por métrica, tabela glass

2. **Login:**
   - Centered layout com logo animado
   - Form glass com inputs dark
   - CTA gradiente com ícone SVG

3. **Registro:**
   - Layout 2 colunas, logo hero
   - Role selection com cards interativos (peer-checked border)
   - Checkmark animado ao selecionar
   - Nota de segurança em card amarelo

4. **Marketplace:**
   - Header com stats (Total, Volume, Status)
   - Grid de cards glass com hover-glow
   - Detalhes em divisores com border-bottom
   - Empty state com emoji grande e CTA
   - Paginação com glass buttons

5. **Component: credit_card.html:**
   - Layout moderno com header (emoji + título)
   - Grid 2x2 para detalhes
   - Badge de status colorido
   - CTA com gradiente e arrow animado

#### Tailwind Config
- **Custom colors:** tucupi-black, tucupi-green (50-900), tucupi-accent
- **Animations:** 6 custom animations (fadeIn, slideUp, scaleIn, glow, etc)
- **Shadow:** glow-green, glow-green-lg, inner-glow
- **Background:** grid-pattern, gradient-radial, gradient-conic

#### Custom CSS
- `.grid-bg`: Background com padrão de grade verde
- `.text-gradient`: Texto com gradiente verde
- `.glass`: Glass morphism com backdrop-filter
- `.hover-glow`: Hover com shadow glow e translateY
- Scrollbar verde customizada

#### Acessibilidade
- HTML lang="pt-BR"
- Meta description
- Labels semânticos
- Alt text em SVGs (via stroke currentColor)
- Focus rings verde em todos inputs
- Contraste WCAG AA+ (verde claro em fundo preto)

#### Performance
- Google Fonts preconnect
- Tailwind CSS minificado (21KB)
- Animações com cubic-bezier otimizadas
- Lazy load de backgrounds com fixed + pointer-events-none

### 2025-10-29 - Melhorias de UX e Segurança
**Dashboard aprimorado e restrição de registro ADMIN**

#### Dashboard Landing Page
- Hero section para usuários não autenticados com CTAs claros
- Botões "Criar conta grátis" e "Já tenho conta" destacados
- Cards explicativos para Produtores (🌱) e Empresas (🏢)
- Design responsivo com Tailwind, cores eco-friendly

#### Segurança no Registro
- Role ADMIN removida do formulário público de registro
- Apenas PRODUCER e COMPANY disponíveis para novos usuários
- Administradores devem ser criados via Django Admin (superuser)
- Nota explicativa no formulário sobre restrição de ADMIN
- 2 novos testes de segurança (47 testes totais, 100% passando)

### 2025-10-29 - Sistema de Transações (Task 4 ✅)
**Compra e transferência de créditos implementada com sucesso!**

#### Models
- Limpeza completa de `transactions/models.py` (removidos duplicados e modelos não utilizados)
- Modelo `Transaction` finalizado com status (PENDING/COMPLETED/CANCELLED)
- Relacionamentos buyer/seller (User) e credit (CarbonCredit) configurados

#### Views e URLs
- `buy_credit` view: processo de compra atômica com validações
  - Somente COMPANY pode comprar
  - Impede compra do próprio crédito
  - Valida status LISTED e listing ativo
  - Transferência de propriedade transacional com `@transaction.atomic()`
- `transaction_history` view: histórico de compras e vendas do usuário
- Rotas configuradas em `credits/urls.py` (`<pk>/buy/`) e `transactions/urls.py` (``→ history)
- URL pattern `/transactions/` ativada em `ecotrade/urls.py`

#### Templates
- `templates/transactions/history.html`: Histórico com estatísticas (total compras/vendas), lista de transações, filtros por comprador/vendedor, badges de status
- `templates/credits/detail.html`: Convertido para `base.html`, botão de compra para empresas com cálculo do total, estilização Tailwind completa

#### Testes (13 novos testes, todos ✅)
- `transactions/tests/test_models.py`: 3 testes (criação, status padrão, str)
- `transactions/tests/test_views.py`: 10 testes
  - `BuyCreditViewTests` (7): autenticação, role COMPANY, sucesso, validação LISTED, dono não compra, POST obrigatório, transação atômica
  - `TransactionHistoryViewTests` (3): autenticação, exibição de transações, estado vazio
- `credits/tests/test_credit_flow.py`: Teste e2e completo (criar → listar → comprar → transferir)

#### Cobertura Total do Projeto
- **45 testes, todos passando (100%)** 🎉
- Task 1 (UI/Tailwind): 9 testes ✅
- Task 2 (Auth/Profile): 14 testes ✅
- Task 3 (Credits/Marketplace): 9 testes ✅
- Task 4 (Transactions): 13 testes ✅
- Task 5 (Dashboard/Admin): 10 testes ✅ (incluído anteriormente)

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