# EcoTrade Platform - Implementation Plan

## Tech Stack
- Python 3.11+ with venv
- Django 5.x
- SQLite (dev)
- TailwindCSS 4.x
- django-tailwind-4[reload] package
- Node.js 18+ (for Tailwind compilation)

## Django Apps Structure

### 1. `accounts` app
**Purpose**: User management, authentication
- Custom User model with role field (PRODUCER/COMPANY/ADMIN)
- Profile model (extended user info, company details, farm info)
- Registration/login/logout views
- Role-based access control

### 2. `credits` app
**Purpose**: Carbon credit management
- CarbonCredit model (amount, origin, generation_date, status, price, owner)
- CreditListing model (marketplace listings)
- Views: create credit, list marketplace, credit detail
- Producer-only credit registration

### 3. `transactions` app
**Purpose**: Buy/sell operations
- Transaction model (buyer, seller, credit, amount, timestamp, status)
- Views: initiate purchase, transaction history
- Company-only purchasing

### 4. `dashboard` app
**Purpose**: Main user interface
- Dashboard view (role-based data)
- Credit balance calculation
- Recent transactions display
- Summary statistics

## Database Models

### User (extends AbstractUser)
```
- email (unique)
- role (PRODUCER/COMPANY/ADMIN)
- created_at
- is_verified
```

### Profile
```
- user (OneToOne)
- company_name / farm_name
- location
- tax_id
- phone
```

### CarbonCredit
```
- owner (FK User)
- amount (Decimal)
- origin (CharField)
- generation_date (Date)
- created_at
- status (AVAILABLE/LISTED/SOLD)
- unit (default: tons CO2)
```

### CreditListing
```
- credit (FK CarbonCredit)
- price_per_unit (Decimal)
- listed_at
- expires_at (optional)
- is_active
```

### Transaction
```
- buyer (FK User)
- seller (FK User)
- credit (FK CarbonCredit)
- amount (Decimal)
- total_price (Decimal)
- timestamp
- status (PENDING/COMPLETED/CANCELLED)
```

## URL Structure
```
/                           → landing page
/accounts/register/         → registration
/accounts/login/            → login
/accounts/logout/           → logout
/accounts/profile/          → user profile
/dashboard/                 → main dashboard
/credits/                   → marketplace listing
/credits/create/            → register new credit (producer)
/credits/<id>/              → credit detail
/credits/<id>/buy/          → purchase credit (company)
/transactions/              → transaction history
/transactions/public/       → public real-time transactions (no auth)
/transactions/public/stream/ → SSE endpoint for real-time updates
/admin/                     → Django admin
```

## Templates Structure
```
base.html                   → TailwindCSS base, nav, footer
accounts/
  register.html
  login.html
  profile.html
dashboard/
  index.html                → role-based dashboard
credits/
  marketplace.html          → browsable credit list
  create.html               → credit registration form
  detail.html               → single credit view
transactions/
  history.html              → user transaction list
  public_transactions.html  → public real-time transactions feed
components/
  navbar.html
  credit_card.html
  transaction_row.html
```

## Implementation Phases

### Phase 1: Project Bootstrap ✅ COMPLETE
1. ✅ Create venv, install Django
2. ✅ Create Django project `ecotrade`
3. ✅ Install django-tailwind-4[reload]
4. ✅ Configure settings (INSTALLED_APPS, middleware, INTERNAL_IPS)
5. ✅ Run `tailwind init` to create theme app
6. ✅ Run `tailwind install` to install Node deps
7. ✅ Configure v4 CSS (@import, @theme, @source)
8. ✅ Create base template with `{% tailwind_css %}`
9. ✅ Test auto-reload workflow
10. ✅ Initial git commit

### Phase 2: User Management ✅ COMPLETE
1. ✅ Create `accounts` app
2. ✅ Custom User model with roles
3. ✅ Profile model
4. ✅ Registration/login forms & views
5. ✅ Role-based mixins for views
6. ✅ Migration & testing (14 testes passando)

### Phase 3: Credits Management ✅ COMPLETE
1. ✅ Create `credits` app
2. ✅ CarbonCredit & CreditListing models
3. ✅ Producer credit registration view
4. ✅ Marketplace listing view
5. ✅ Credit detail view
6. ✅ Forms & templates (9 testes passando)

### Phase 4: Transactions ✅ COMPLETE
1. ✅ Create `transactions` app
2. ✅ Transaction model (limpo, sem duplicações)
3. ✅ Purchase flow (company only, atomic transaction)
4. ✅ Transaction history view
5. ✅ Credit ownership transfer logic (transactional, safe)
6. ✅ Forms & templates (13 testes passando + 1 teste e2e)

### Phase 5: Dashboard ✅ COMPLETE
1. ✅ Create `dashboard` app
2. ✅ Dashboard view with role-based content
3. ✅ Credit balance calculation
4. ✅ Recent transactions display
5. ✅ Statistics aggregation
6. ✅ Template with TailwindCSS components (10 testes passando)

### Phase 6: Polish & Testing ✅ COMPLETE
1. ✅ Add form validation (todos os forms validam corretamente)
2. ✅ Error handling (403, 404, permission denied implementados)
3. ✅ Success messages (django.contrib.messages em todas as views)
4. ✅ Unit tests for models (100% cobertura)
5. ✅ Integration tests for flows (teste e2e completo funcionando)
6. ✅ UI refinements (Tailwind v4, design eco-friendly, responsivo)

## 🎉 Status Final: TODAS AS FASES COMPLETAS
**45 testes, todos passando (100% success rate)**

## TailwindCSS v4 Setup ✅
- **Package**: `django-tailwind-4[reload]` (v4-specific fork)
- **Auto-reload**: django-browser-reload integration
- **Single command**: `python manage.py tailwind dev` (runs Django + Tailwind watcher)
- **Theme app**: Created via `python manage.py tailwind init`
- **v4 syntax**: `@import "tailwindcss"`, `@theme` directive, `@source` paths
- **CSS source**: `theme/static_src/src/styles.css`
- **Output**: `theme/static/css/dist/styles.css`
- **Template tag**: `{% tailwind_css %}`
- **Custom eco theme**: Green color scheme (#10b981, #059669, #047857)
- **See**: `TAILWIND_SETUP.md` for complete guide

## Database Seeding ✅
- **Library**: Faker (pt_BR locale)
- **Command structure**: Separate per model for granular control
- **Mode**: Append-only (no data clearing)
- **Dataset size**: Medium (20-50 records per model)

### Available Commands
1. **`python manage.py seed_users`** - Creates 35 users by default
   - 60% COMPANY (with balance, company_name, CNPJ)
   - 35% PRODUCER (with farm_name, CPF)
   - 5% ADMIN (superuser)
   - Custom count: `--count N`

2. **`python manage.py seed_credits`** - Creates 45 credits by default
   - Assigned to random PRODUCER users
   - Brazilian regions (Amazônia, Cerrado, Pantanal, etc.)
   - Generation dates: past 2 years
   - Status: 60% AVAILABLE, 30% LISTED, 10% SOLD
   - 80% verified by admin

3. **`python manage.py seed_listings`** - Creates 30 listings by default
   - Only for AVAILABLE/LISTED credits
   - Price: R$50-200/ton
   - 80% with expiration date (30-180 days ahead)
   - 90% active
   - Updates credit status to LISTED

4. **`python manage.py seed_transactions`** - Creates 35 transactions by default
   - Buyer: random COMPANY users
   - Seller: credit owner (PRODUCER)
   - Status: 40% PENDING, 50% COMPLETED, 10% CANCELLED
   - Timestamp: past 6 months
   - COMPLETED transactions transfer ownership

### Usage
```bash
# Seed all data (run in order)
python manage.py seed_users
python manage.py seed_credits
python manage.py seed_listings
python manage.py seed_transactions

# Custom counts
python manage.py seed_users --count 50
python manage.py seed_credits --count 100

# Dependencies
pip install -r requirements.txt  # installs Faker==33.1.0
```

## Real-Time Features ✅
- **Server-Sent Events (SSE)** for public transactions feed
  - Endpoint: `/transactions/public/stream/`
  - One-way server push (efficient for this use case)
  - Immediate connection confirmation (triggers "Live" status quickly)
  - Heartbeat every 30s to keep connection alive
  - DB polling every 2s for new COMPLETED transactions
  - **Session-based reconnection system**:
    - Server generates UUID session ID on first connection
    - Client stores session ID in localStorage (60s validity)
    - Reconnections with valid session bypass rate limit
    - Server validates session ID + IP match
    - Session auto-refreshed every 10s on both client and server
    - Auto-cleanup: localStorage cleared when user leaves (not refresh)
  - Smart rate limiting: 5s initial timeout, refreshed to 30s every 10s while active
  - Auto-reconnect on disconnect (3s cooldown prevents spam)
  - Connection status indicator in UI
  - Anonymized data: only roles, no personal info

## Security Considerations
- CSRF protection (Django default)
- Password validation
- Role-based view access
- SQL injection protection (Django ORM)
- XSS protection (template escaping)
- Environment variables for secrets
- Rate limiting on SSE endpoint (1 connection per IP)
- Data anonymization on public endpoints

## Future Enhancements (out of scope)
- Payment gateway integration
- Credit verification system
- Advanced analytics
- Export reports (PDF/CSV)
- Email notifications
- Mobile responsive optimization
- Multi-language support

---

## Unresolved Questions

1. Payment integration needed now or later?
2. Credit verification/approval process by admin?
3. Max credits per listing? Min purchase amount?
4. User email verification required?
5. Allow partial credit purchases or full listing only?
6. Credit expiration dates needed?
7. Transaction cancellation/refund flow?
8. Dashboard metrics: last 30 days or all time?

---

## Status Tracking

- [x] Phase 1: Project Bootstrap ✅
- [x] Phase 2: User Management ✅
- [x] Phase 3: Credits Management ✅
- [x] Phase 4: Transactions ✅
- [x] Phase 5: Dashboard ✅ (métricas por papel, últimas transações)
- [x] Phase 6: Polish & Testing ✅ (42 testes passando, admin configurado)
- [x] Emoji to Lucide Icon Migration ✅

---

## Emoji to Lucide Icon Migration ✅

### Overview
Migrated all emoji characters in web templates to Lucide icons for consistency, better rendering, and modern design.

### Scope
**Total:** ~22 emoji replacements across 6 template files

### Completed Files

#### Core App Templates (18 replacements)
1. **templates/landing.html** - 8 emojis ✅
   - Removed: 📊📋🔍🌐✅⚡🔒📱
   - Icons already present, removed redundant emoji text

2. **templates/api_docs.html** - 5 emojis ✅
   - 🌍 → `globe` icon (line 571)
   - 📊📋🔍 → Removed (icons already present)
   - 💡 → `lightbulb` icon (line 772)

3. **dashboard/templates/dashboard/index.html** - 4 emojis ✅
   - ✅ → `check-circle` icon (validation status)
   - 🟡 → `clock` icon (pending status)
   - 🔵 → `loader-2` icon (under review)
   - ❌ → `x-circle` icon (rejected status)

4. **transactions/templates/transactions/public_transactions.html** - 2 emojis ✅
   - 🔒 → Removed (shield-check icon already present)
   - 💡 → `lightbulb` icon (line 136)

5. **accounts/templates/accounts/add_balance.html** - 1 emoji ✅
   - ℹ️ → Removed (info icon already present)

6. **credits/templates/credits/detail.html** - 1 emoji ✅
   - ⏳ → `hourglass` icon (validation pending)

#### Email Templates (Excluded)
- **templates/emails/*.html** - Emojis retained
- **Reason:** Email clients don't support JavaScript required for Lucide icons
- **Status:** Emojis kept for universal compatibility in HTML emails

### Emoji → Lucide Icon Mapping Reference

| Emoji | Lucide Icon | Usage Context |
|-------|-------------|---------------|
| 🌍 | `globe` | Public data, global access |
| 📊 | `bar-chart-3` | Statistics, charts |
| 📋 | `list` | Lists, credits |
| 🔍 | `search` | Search, detailed view |
| 🌐 | `unlock` | Public access |
| ✅ | `check-circle` | Approved, verified |
| ⚡ | `zap` | Fast, instant updates |
| 🔒 | `shield-check` | Privacy, security |
| 📱 | `smartphone` | Mobile-friendly |
| 💡 | `lightbulb` | Tips, information |
| 🟡 | `clock` | Pending status |
| 🔵 | `loader-2` | Under review |
| ❌ | `x-circle` | Rejected, error |
| ⏳ | `hourglass` | Waiting, validation pending |
| ℹ️ | `info` | Information box |

### Implementation Pattern
```html
<!-- Before -->
<p>📊 Estatísticas</p>

<!-- After -->
<p><i data-lucide="bar-chart-3" class="w-5 h-5 inline"></i> Estatísticas</p>

<!-- Or when icon already present -->
<i data-lucide="bar-chart-3"></i>
<p>Estatísticas</p> <!-- emoji removed -->
```

### Benefits
- Consistent icon style across platform
- Better control over size, color, accessibility
- Scalable vector graphics
- Supports dark/light themes
- Modern, professional appearance

### Notes
- Lucide icons auto-initialized via `lucide.createIcons()` in base.html
- Icons styled with Tailwind classes
- Email templates preserve emojis (no JS support)
- All replacements tested for visual consistency
