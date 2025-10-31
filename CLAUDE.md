# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EcoTrade: Carbon credit marketplace platform connecting producers (farmers) with companies for regional carbon credit trading.

**Tech Stack**: Django 5.x, Python 3.11+, TailwindCSS 4.x (via django-tailwind-4[reload]), SQLite (dev), Node.js 18+

## Architecture

### 4-App Structure

1. **`accounts`** - User mgmt w/ custom User model (role: PRODUCER/COMPANY/ADMIN), Profile, auth views
2. **`credits`** - CarbonCredit & CreditListing models, marketplace, producer registration
3. **`transactions`** - Transaction model, purchase flow, ownership transfer
4. **`dashboard`** - Role-based UI, balance calc, recent activity, stats

### Key Models & Relationships

- **User** (AbstractUser) → role field, one-to-one Profile
- **CarbonCredit** → owner (FK User), status (AVAILABLE/LISTED/SOLD)
- **CreditListing** → credit (FK CarbonCredit), price_per_unit
- **Transaction** → buyer/seller (FK User), credit (FK CarbonCredit), status (PENDING/COMPLETED/CANCELLED)

### Business Flow

1. Producer registers credits (origin, amount, gen_date)
2. Producer creates listings w/ price
3. Company browses marketplace
4. Company purchases → Transaction created
5. Credit ownership transfers on completion

### Role-Based Access

- **PRODUCER**: register credits, create listings, view own credits/sales
- **COMPANY**: browse marketplace, purchase credits, view purchases
- **ADMIN**: Django admin access

## Development Commands

### Environment Setup
```bash
# Create venv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install deps
pip install -r requirements.txt

# Setup Tailwind v4
python manage.py tailwind install
```

### Running Dev Server
```bash
# Single command (recommended) - runs Django + Tailwind watcher + auto-reload
python manage.py tailwind dev

# Alternative: Separate terminals
# Terminal 1: Tailwind watcher only
python manage.py tailwind start
# Terminal 2: Django server
python manage.py runserver
```

### Database
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Testing
```bash
# All tests
python manage.py test

# Specific app
python manage.py test accounts

# Specific test
python manage.py test accounts.tests.TestUserModel.test_role_assignment
```

### Seeding Data
```bash
# Basic seeding (run in order)
python manage.py seed_users --count 20        # Creates users (producers/companies/admins)
python manage.py seed_credits --count 30      # Creates carbon credits with GENESIS history
python manage.py seed_listings --count 15     # Creates marketplace listings
python manage.py seed_transactions --count 10 # Creates transactions with SALE history

# Advanced: Multi-hop ownership chains (blockchain demo)
python manage.py seed_ownership_transfers --chains 5 --depth 4
# Creates credits that change hands multiple times
# Perfect for demonstrating blockchain-style history

# View ownership statistics
python manage.py show_ownership_stats
# Shows: total history entries, transfers, most-transferred credits

# NOTE: All ownership changes are automatically tracked via Django signals
# View any credit history at: /credits/<id>/history/
```

## TailwindCSS v4 Integration

- **Package**: django-tailwind-4[reload] (v4-specific fork)
- **Theme app**: `theme/` (created via `tailwind init`)
- **v4 CSS source**: `theme/static_src/src/styles.css` (uses `@import "tailwindcss"`, `@theme`, `@source`)
- **Compiled output**: `theme/static/css/dist/styles.css`
- **Template tag**: `{% load tailwind_tags %}` → `{% tailwind_css %}`
- **Auto-reload**: django-browser-reload (automatic page refresh on changes)
- **Color scheme**: Eco green theme (#10b981, #059669, #047857)
- **Full guide**: See `TAILWIND_SETUP.md` for complete v4 setup instructions

### Tailwind v4 Differences
- Uses `@import "tailwindcss"` instead of `@tailwind` directives
- Custom theme via `@theme { --color-name: value }` not `tailwind.config.js`
- Content paths via `@source` directive in CSS (optional config.js)
- Single `tailwind dev` command replaces dual terminal setup

## Icons (Lucide, Not Emojis)

**IMPORTANT**: Use Lucide icons in all web templates. DO NOT use emoji characters.

### Basic Usage
```html
<!-- Standard icon -->
<i data-lucide="check-circle" class="w-5 h-5 text-green-500"></i>

<!-- Inline with text -->
<span class="flex items-center gap-2">
  <i data-lucide="globe" class="w-4 h-4"></i> Public Data
</span>
```

### Common Mappings
```
Status:     ✅ → check-circle  |  ❌ → x-circle  |  ⏳ → hourglass
Workflow:   🟡 → clock         |  🔵 → loader-2  |  ✅ → check-circle
Info:       💡 → lightbulb     |  ℹ️ → info      |  🔒 → shield-check
Data:       📊 → bar-chart-3   |  📋 → list      |  🔍 → search
Global:     🌍 → globe         |  🌐 → unlock    |  📱 → smartphone
Action:     ⚡ → zap           |  🎯 → target    |  🔧 → wrench
```

### Icon Sizes (Tailwind)
- `w-3 h-3` - 12px (badges)
- `w-4 h-4` - 16px (inline text)
- `w-5 h-5` - 20px (buttons, standard)
- `w-6 h-6` - 24px (headers)
- `w-8 h-8`+ - 32px+ (heroes)

### Email Templates Exception
Email templates (templates/emails/\*.html) MUST use emojis since Lucide requires JavaScript:
```html
<!-- templates/emails/base.html -->
<h1>🌱 EcoTrade</h1>  <!-- CORRECT for email -->
```

### Dynamic Icon Initialization
When adding icons via JavaScript (SSE, AJAX):
```javascript
// After inserting HTML with icons
lucide.createIcons();
```

**See**: PLAN.md "Emoji to Lucide Icon Migration" for complete reference | https://lucide.dev/icons/ for icon search

## Implementation Status

See `PLAN.md` for phase tracking. Update status checkboxes as phases complete.

**Current phase**: See PLAN.md "Status Tracking" section

## Project Conventions

- **Auth**: Django built-in (email/password)
- **DB**: SQLite for dev (plan migration path for prod)
- **Templates only**: No REST API initially
- **Marketplace model**: Listings browsed, full credit purchases
- **CHANGELOG.md**: Update on major changes/refactors
