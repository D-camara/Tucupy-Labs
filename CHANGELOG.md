# Changelog

## 2025-10-30

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
