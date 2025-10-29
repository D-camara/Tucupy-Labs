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
components/
  navbar.html
  credit_card.html
  transaction_row.html
```

## Implementation Phases

### Phase 1: Project Bootstrap ⏳
1. Create venv, install Django
2. Create Django project `ecotrade`
3. Install django-tailwind-4[reload]
4. Configure settings (INSTALLED_APPS, middleware, INTERNAL_IPS)
5. Run `tailwind init` to create theme app
6. Run `tailwind install` to install Node deps
7. Configure v4 CSS (@import, @theme, @source)
8. Create base template with `{% tailwind_css %}`
9. Test auto-reload workflow
10. Initial git commit

### Phase 2: User Management
1. Create `accounts` app
2. Custom User model with roles
3. Profile model
4. Registration/login forms & views
5. Role-based mixins for views
6. Migration & testing

### Phase 3: Credits Management
1. Create `credits` app
2. CarbonCredit & CreditListing models
3. Producer credit registration view
4. Marketplace listing view
5. Credit detail view
6. Forms & templates

### Phase 4: Transactions
1. Create `transactions` app
2. Transaction model
3. Purchase flow (company only)
4. Transaction history view
5. Credit ownership transfer logic
6. Forms & templates

### Phase 5: Dashboard
1. Create `dashboard` app
2. Dashboard view with role-based content
3. Credit balance calculation
4. Recent transactions display
5. Statistics aggregation
6. Template with TailwindCSS components

### Phase 6: Polish & Testing
1. Add form validation
2. Error handling
3. Success messages
4. Unit tests for models
5. Integration tests for flows
6. UI refinements

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

## Security Considerations
- CSRF protection (Django default)
- Password validation
- Role-based view access
- SQL injection protection (Django ORM)
- XSS protection (template escaping)
- Environment variables for secrets

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

- [ ] Phase 1: Project Bootstrap
- [ ] Phase 2: User Management
- [ ] Phase 3: Credits Management
- [ ] Phase 4: Transactions
- [ ] Phase 5: Dashboard
- [ ] Phase 6: Polish & Testing
