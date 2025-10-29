# Changelog

All notable changes to the EcoTrade platform.

## [Unreleased]

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
