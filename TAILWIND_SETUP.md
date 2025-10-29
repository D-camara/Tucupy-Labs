# Tailwind CSS v4 Setup Guide - EcoTrade

## Decision: Use django-tailwind-4[reload]

**Package**: `django-tailwind-4` (fork specifically for v4)
**Extras**: `[reload]` for django-browser-reload integration

### Why this approach?
- Native v4 support out of the box
- Single command dev workflow (`tailwind dev`)
- Auto browser reload (no manual refresh)
- Hot CSS reload on template/config changes
- Simpler than manual Tailwind CLI setup
- No webpack complexity

## Implementation Steps

### 1. Install Package
```bash
# Activate venv first
source venv/bin/activate

# Install with reload support
pip install 'django-tailwind-4[reload]'

# Freeze requirements
pip freeze > requirements.txt
```

### 2. Django Settings Configuration

**Add to `INSTALLED_APPS` in `ecotrade/settings.py`:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'tailwind',
    'django_browser_reload',  # For auto-reload
    # theme app will be added after init
]
```

**Add middleware for browser reload:**
```python
MIDDLEWARE = [
    # ... existing middleware
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]
```

**Set Tailwind app name:**
```python
TAILWIND_APP_NAME = 'theme'
```

**Configure internal IPs (for reload to work):**
```python
INTERNAL_IPS = [
    "127.0.0.1",
]
```

### 3. Initialize Theme App
```bash
# Create theme app (default name: theme)
python manage.py tailwind init

# Or specify custom name:
# python manage.py tailwind init --app-name custom_theme
```

**This creates:**
- `theme/` app directory
- `theme/static_src/` for source files
- `theme/templates/` for base template
- `package.json` with Tailwind v4
- Tailwind v4 config files

**Add theme to INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'tailwind',
    'theme',  # Add this
    'django_browser_reload',
]
```

### 4. Install Node Dependencies
```bash
# Downloads and installs Tailwind v4 and dependencies
python manage.py tailwind install
```

### 5. Template Setup

**Base template location**: `theme/templates/base.html`

**Load Tailwind in templates:**
```django
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EcoTrade{% endblock %}</title>
    {% tailwind_css %}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**Configure template dirs in `settings.py`:**
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Project-wide templates
            # theme templates auto-discovered
        ],
        # ... rest of config
    },
]
```

### 6. Tailwind v4 CSS Configuration

**Location**: `theme/static_src/src/styles.css`

**Tailwind v4 syntax:**
```css
@import "tailwindcss";

/* Custom theme using v4 @theme directive */
@theme {
  /* Eco color scheme */
  --color-eco-primary: #10b981;
  --color-eco-secondary: #059669;
  --color-eco-dark: #047857;
  --color-eco-light: #34d399;

  /* Custom spacing if needed */
  --spacing-18: 4.5rem;
}

/* Global styles */
@layer base {
  body {
    @apply text-gray-900 bg-gray-50;
  }
}

/* Custom component classes */
@layer components {
  .btn-primary {
    @apply bg-eco-primary text-white px-4 py-2 rounded-lg hover:bg-eco-dark transition-colors;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}
```

### 7. Configure Content Sources

**Tailwind v4 uses `@source` directive** (not `content` in config)

**In `theme/static_src/src/styles.css`:**
```css
@import "tailwindcss";

/* Tell Tailwind where to find classes */
@source "../templates";  /* theme templates */
@source "../../templates";  /* project templates */
@source "../../**/templates";  /* all app templates */

@theme {
  /* ... theme config */
}
```

**Alternative: Use `tailwind.config.js` (v4 style):**
```javascript
// theme/static_src/tailwind.config.js
export default {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
}
```

### 8. Development Workflow

**Single command for dev:**
```bash
python manage.py tailwind dev
```

**This runs:**
- Tailwind watcher (rebuilds CSS on changes)
- Django dev server (port 8000)
- Browser auto-reload on file changes

**Alternative: Separate terminals**
```bash
# Terminal 1: Tailwind watch only
python manage.py tailwind start

# Terminal 2: Django server
python manage.py runserver
```

### 9. Production Build

**Build minified CSS:**
```bash
python manage.py tailwind build
```

**Output**: `theme/static/css/dist/styles.css` (minified)

**Collect static files:**
```bash
python manage.py collectstatic
```

## Project Structure After Setup

```
django-ecotrade/
  theme/                          # Created by tailwind init
    static/
      css/dist/
        styles.css                # Compiled output
    static_src/
      src/
        styles.css                # Source CSS (v4 syntax)
      tailwind.config.js          # Optional v4 config
      package.json                # Tailwind v4 deps
      node_modules/
    templates/
      base.html                   # Base template
  templates/                      # Project templates
    components/
      navbar.html
    accounts/
      register.html
    dashboard/
      index.html
  ecotrade/
    settings.py                   # Tailwind config added
    urls.py                       # Browser reload URL added
```

## URLs Configuration

**Add browser reload URL in `ecotrade/urls.py`:**
```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path("__reload__/", include("django_browser_reload.urls")),
]
```

## Testing the Setup

### 1. Start dev server
```bash
python manage.py tailwind dev
```

### 2. Create test template
**`templates/test.html`:**
```django
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto p-8">
  <h1 class="text-4xl font-bold text-eco-primary">EcoTrade Test</h1>
  <div class="card mt-4">
    <p class="text-gray-700">Tailwind v4 is working!</p>
    <button class="btn-primary mt-4">Test Button</button>
  </div>
</div>
{% endblock %}
```

### 3. Add view and URL
```python
# Quick test view
from django.shortcuts import render

def test_view(request):
    return render(request, 'test.html')
```

### 4. Test auto-reload
- Modify template → Save → Browser auto-refreshes
- Add new Tailwind class → Save CSS → Styles rebuild
- No manual refresh needed

## Customization for EcoTrade

### Eco Theme Colors
```css
@theme {
  --color-eco-primary: #10b981;      /* Green-500 */
  --color-eco-secondary: #059669;    /* Green-600 */
  --color-eco-dark: #047857;         /* Green-700 */
  --color-eco-light: #34d399;        /* Green-400 */
  --color-eco-lighter: #6ee7b7;      /* Green-300 */

  --color-carbon: #1f2937;           /* Gray-800 for carbon theme */
  --color-earth: #92400e;            /* Brown-700 */
}
```

### Reusable Components
```css
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-all;
  }

  .btn-primary {
    @apply btn bg-eco-primary text-white hover:bg-eco-dark;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-800 hover:bg-gray-300;
  }

  .credit-card {
    @apply bg-white rounded-xl shadow-lg p-6 border-l-4 border-eco-primary;
  }

  .stat-box {
    @apply bg-gradient-to-br from-eco-light to-eco-primary text-white p-6 rounded-lg;
  }
}
```

## Common Issues & Solutions

### Issue: Styles not updating
**Solution**:
- Check `@source` paths in styles.css
- Verify template is in scanned directory
- Restart `tailwind dev`

### Issue: Browser not auto-reloading
**Solution**:
- Check `INTERNAL_IPS` in settings
- Verify `django_browser_reload` in INSTALLED_APPS
- Check middleware order

### Issue: Node.js version error
**Solution**:
- Requires Node.js 18+
- Update: `nvm install 22` or download from nodejs.org

## Next Steps

1. ✅ Setup complete
2. Create navbar component
3. Build registration form
4. Style dashboard
5. Design credit cards
6. Build marketplace UI

## References

- [django-tailwind-4 docs](https://django-tailwind-4.readthedocs.io/)
- [Tailwind CSS v4 docs](https://tailwindcss.com/docs/v4-beta)
- [django-browser-reload](https://github.com/adamchainz/django-browser-reload)
