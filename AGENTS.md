# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex CLI, etc.) working in this repository. Pair this with CLAUDE.md and PLAN.md for architecture and phase details.

This file is intentionally practical and scoped to this project’s stack and goals.

## Scope & Precedence

- Scope: Applies to the entire repository tree unless a more-deeply-nested AGENTS.md overrides portions for that subtree.
- Precedence: Direct user/system instructions override this file. If instructions conflict across AGENTS.md files, the closer (deeper) file wins for files under its directory.
- Changes: If you alter conventions or workflows, update this file and add an entry to CHANGELOG.md.

## Quick Project Facts

- Name: EcoTrade – regional carbon credit marketplace
- Stack: Django 5.x, Python 3.11+, TailwindCSS 4.x (via django-tailwind-4[reload]), SQLite (dev)
- Apps: accounts, credits, transactions, dashboard (see CLAUDE.md and PLAN.md)
- Roles: PRODUCER, COMPANY, ADMIN with role-based access throughout

Authoritative project context lives in:

- CLAUDE.md – overview, architecture, commands
- PLAN.md – detailed implementation plan and phases
- CHANGELOG.md – notable changes and refactors

## Repository Workflow

Environment

1) Create and activate a Python 3.11+ venv.
2) Install dependencies from requirements.txt.
3) Initialize Tailwind via django-tailwind when the Django project exists.

Common commands (see CLAUDE.md for more):

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Django server
python manage.py runserver

# Tailwind
# Recommended single-command dev (Django + Tailwind + reload)
python manage.py tailwind dev
# Alternative split workflow
python manage.py tailwind install
python manage.py tailwind start

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Tests
python manage.py test
```

Process

1) Follow PLAN.md phases; do not leapfrog scope without approval.
2) Keep changes minimal and focused; prefer small, verifiable steps.
3) Update PLAN.md status and CHANGELOG.md when completing meaningful work.
4) Prefer standard Django patterns over custom abstractions unless required.

## Coding Conventions

General

- Python style: PEP 8, descriptive names, no one-letter vars.
- Use type hints on public functions, model methods, and service helpers.
- Keep functions short and single-purpose; extract helpers when useful.
- Docstrings for modules, complex functions, and non-trivial classes.

Django

- Apps: `accounts`, `credits`, `transactions`, `dashboard` (plus `theme` for Tailwind).
- Views: prefer class-based views; use Django generic views where applicable.
- Forms: use Django Form/ModelForm for validation; add `clean_*` methods as needed.
- Templates: keep presentation logic in templates; avoid business logic in templates.
- URLs: group by app; keep paths stable and human-readable (see PLAN.md URLs).
- Static: Tailwind via `django-tailwind` in a `theme` app; avoid inline styles.

Models & Migrations

- Create migrations for every model change; never hand-edit schema migrations.
- Use `choices`/enums for status/role fields; store compact values, display labels in UI.
- Monetary/quantity values: use `DecimalField` with explicit `max_digits` and `decimal_places`.
- Datetimes: use timezone-aware fields (`USE_TZ=True` expected); prefer `auto_now_add/auto_now` where appropriate.
- Relationships: define `related_name`, consider `on_delete` carefully; avoid cascading deletes that surprise users.

Security & Access

- Enforce role-based access on views and actions (PRODUCER/COMPANY/ADMIN).
- Always check object ownership for mutating actions.
- Rely on Django’s CSRF, auth, and template auto-escaping; avoid raw SQL.

## Architecture Rules (from CLAUDE.md)

- accounts: custom User (role), Profile, auth views
- credits: CarbonCredit, CreditListing, marketplace listing/browse
- transactions: Transaction model, purchase flow, ownership transfer
- dashboard: role-based UI, balances, recent activity, stats

Business flow (high level):

1) Producer registers credits → 2) Producer lists credits → 3) Company browses → 4) Company purchases (Transaction) → 5) Ownership transfers on completion

## TailwindCSS

- Use `django-tailwind-4[reload]` to create a `theme` app.
- v4 CSS authored in `theme/static_src/src/styles.css` using `@import "tailwindcss"`, `@theme`, and `@source`.
- Content scanning via `@source` in CSS (optional: `theme/static_src/tailwind.config.js`).
- Load CSS in templates with `{% load tailwind_tags %}` and `{% tailwind_css %}`.
- Auto-reload via `django-browser-reload`; prefer `python manage.py tailwind dev` during development.
- Eco/green color scheme; semantic HTML with accessible components (labels, focus states, contrast).

## Icons & Visual Elements

**Use Lucide Icons, Not Emojis** (for web templates)

- **Library**: Lucide Icons (loaded via CDN in base.html)
- **Syntax**: `<i data-lucide="icon-name" class="w-5 h-5"></i>`
- **Initialization**: Icons auto-initialize via `lucide.createIcons()` in base template
- **NEVER use emojis** in web templates (HTML served to browsers)
- **Exception**: Email templates ONLY (email clients don't support JavaScript/Lucide)

Common Icon Mappings (emoji → Lucide):
```
✅ → check-circle       🔍 → search           💡 → lightbulb
❌ → x-circle           📊 → bar-chart-3      🔒 → shield-check
⏳ → hourglass          📋 → list             🌍 → globe
🟡 → clock (pending)    📱 → smartphone       ⚡ → zap
🔵 → loader-2 (review)  ℹ️ → info             🌐 → unlock
```

Implementation Pattern:
```html
<!-- CORRECT: Lucide icon with Tailwind sizing -->
<i data-lucide="check-circle" class="w-5 h-5 text-green-500"></i>

<!-- CORRECT: Inline icon with text -->
<p class="flex items-center gap-2">
  <i data-lucide="globe" class="w-4 h-4"></i> Public Data
</p>

<!-- WRONG: Don't use emojis in web templates -->
<p>✅ Approved</p>  <!-- NO! -->

<!-- EXCEPTION: Email templates only -->
<!-- templates/emails/base.html -->
<h1>🌱 EcoTrade</h1>  <!-- OK for emails -->
```

Icon Sizing with Tailwind:
- `w-3 h-3` - Small (12px) - inline badges, compact UI
- `w-4 h-4` - Small+ (16px) - inline text, list items
- `w-5 h-5` - Medium (20px) - buttons, headers, standard UI
- `w-6 h-6` - Large (24px) - prominent features
- `w-8 h-8`+ - XL (32px+) - hero sections, large cards

When adding new icons:
1. Search Lucide docs: https://lucide.dev/icons/
2. Use semantic names (prefer `check-circle` over `checkmark`)
3. Add ARIA labels for accessibility when icon-only
4. Style with Tailwind color utilities (text-green-500, etc.)
5. Initialize dynamic icons: call `lucide.createIcons()` after DOM insertion

See PLAN.md "Emoji to Lucide Icon Migration" section for complete mapping reference.

## Testing

- Use `python manage.py test` for the suite; keep tests close to apps (`<app>/tests/`).
- Models: test constraints, choices, simple method behavior.
- Views: test permissions, redirects, and success paths.
- Flows: add integration tests for purchase/ownership transfer.
- Avoid network calls and external services in tests.

## Safety & Constraints

- Target: Python 3.11+, Django 5.x, SQLite for dev.
- No external network dependencies without explicit approval.
- Keep dependencies minimal; prefer built-in Django/stdlib first.
- Do not introduce payment gateways or REST API unless explicitly in scope.

## When In Doubt

- Consult CLAUDE.md for architecture/flow, PLAN.md for scope ordering.
- Prefer the simplest approach that satisfies requirements.
- Ask for clarification if a requirement is ambiguous; otherwise proceed conservatively.

## Checklists

Adding/Changing a Model

- [ ] Fields defined with types, verbose_name, help_text
- [ ] `choices`/constants for enumerations
- [ ] `related_name` and `on_delete` set deliberately
- [ ] Migration created and applied locally
- [ ] Unit tests updated/added

Adding a View/URL/Template

- [ ] Permission/role checks enforced
- [ ] Forms validate and show helpful errors
- [ ] Template accessible, responsive with Tailwind
- [ ] URL added, named, and referenced consistently
- [ ] Tests for allowed/denied access and happy path

State/Status Changes (e.g., purchase)

- [ ] Transactionally safe (atomic where needed)
- [ ] Ownership, balances, and statuses updated consistently
- [ ] Idempotency considered for repeat submissions
- [ ] User feedback via messages
- [ ] Tests cover edge cases
