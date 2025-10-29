# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EcoTrade: Carbon credit marketplace platform connecting producers (farmers) with companies for regional carbon credit trading.

**Tech Stack**: Django 5.x, Python 3.11+, TailwindCSS 3.x (via django-tailwind), SQLite (dev)

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

# Setup Tailwind (after django-tailwind installed)
python manage.py tailwind install
```

### Running Dev Server
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Tailwind watcher
python manage.py tailwind start
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

## TailwindCSS Integration

- **Package**: django-tailwind creates `theme` app
- **Config**: `theme/static_src/tailwind.config.js`
- **Styles**: `theme/static_src/src/styles.css`
- **Color scheme**: Green/eco theme
- **JIT mode**: Enabled for faster builds

## Implementation Status

See `PLAN.md` for phase tracking. Update status checkboxes as phases complete.

**Current phase**: See PLAN.md "Status Tracking" section

## Project Conventions

- **Auth**: Django built-in (email/password)
- **DB**: SQLite for dev (plan migration path for prod)
- **Templates only**: No REST API initially
- **Marketplace model**: Listings browsed, full credit purchases
- **CHANGELOG.md**: Update on major changes/refactors
