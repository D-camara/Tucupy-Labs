# Changelog

All notable changes to the EcoTrade platform.

## [Unreleased]

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
