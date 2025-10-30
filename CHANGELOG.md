# Changelog

## 2025-10-30

### Added
- **Public Real-Time Transactions Page**: Live transparency feed for marketplace activity
  - New public page (`/transactions/public/`) - no auth required
  - Server-Sent Events (SSE) for real-time updates
  - Shows last 10 COMPLETED transactions with auto-refresh
  - Anonymized data: only participant roles (Company/Producer), no personal info
  - **Session-based reconnection system**:
    - Unique session ID generated per connection, stored in localStorage
    - Reconnections within 60s bypass rate limit (allows page refresh)
    - Session auto-refreshed every 10s while active
    - Auto-cleanup when user leaves (not just refresh)
  - Smart rate limiting: 5s initial timeout, auto-refreshes to 30s while connected
  - Immediate connection confirmation (fast "Live" status update)
  - Connection status indicator with auto-reconnect (3s cooldown)
  - Relative timestamps ("2 mins ago")
  - Main nav link added for visibility
  - Features: live updates, privacy protection, full transparency, seamless reconnection

## 2025-10-30

### Changed
- **Tailwind v4 Theme Migration**: Migrated theme config from JS to CSS for v4 compatibility
  - Moved all theme extensions from `tailwind.config.js` to `styles.css` using `@theme` directive
  - Converted colors (Tucupi brand palette), fonts, animations, shadows to CSS variables
  - Added custom keyframes (`fadeIn`, `slideUp`, `slideDown`, `scaleIn`, `glow`) as standard CSS
  - Custom background utilities (`bg-gradient-radial`, `bg-gradient-conic`, `bg-grid-pattern`) in `@layer utilities`
  - Retained legacy `eco-*` color aliases for backward compatibility
- **Icon Migration**: Replaced all emojis (19 unique) with Lucide SVG icons
  - Migrated 12 template files across all apps
  - Added Lucide CDN to `base.html` with auto-initialization
  - Icon mappings: 🌱→sprout, 💵→banknote, 🏢→building-2, 📊→bar-chart-3, ✓→check, 🔗→link, 🌍→globe, 📜→scroll-text, 🔒→lock, 💰→wallet, 🛒→shopping-cart, 📦→package, 🟢→circle (filled), 🌾→wheat, 👤→user, 📥→download, 📤→upload, ⏳→clock, ✗→x
  - Benefits: better consistency, accessibility, customizability
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
