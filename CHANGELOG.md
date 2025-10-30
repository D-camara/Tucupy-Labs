# Changelog

## 2025-10-30

### Changed
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
- **daisyUI v5**: Installed Tailwind component library for enhanced UI components
  - Added daisyUI npm package (latest version)
  - Configured via `@plugin` directive in styles.css (Tailwind v4 syntax)
  - Compatible with existing custom components
