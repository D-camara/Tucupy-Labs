from pathlib import Path
import os
from dotenv import load_dotenv
import django_stubs_ext

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

django_stubs_ext.monkeypatch()

BASE_DIR = Path(__file__).resolve().parent.parent

# WARNING: Replace for production via environment variable
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS: list[str] = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Tailwind & reload
    "tailwind",
    "django_browser_reload",
    # Local apps
    "theme",
    "accounts",
    "credits",
    "transactions",
    "dashboard",
    "api",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]


ROOT_URLCONF = "ecotrade.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "ecotrade.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom user model must be set before first migration
AUTH_USER_MODEL = "accounts.User"

# Tailwind configuration
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = [
    "127.0.0.1",
]

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

# Email backend - SMTP real (Gmail) para envio local
# Nota: Projeto funciona 100% localmente, emails serão enviados de verdade
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"  # SMTP real por padrão
    # "django.core.mail.backends.console.EmailBackend"  # Descomente para debug (imprime no terminal)
)

# Configurações SMTP (Gmail)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False") == "True"

# Credenciais (usar variáveis de ambiente em produção)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "tucupilabs@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")  # Senha de app do Gmail

# Email padrão para envio
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Tucupi Labs <tucupilabs@gmail.com>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL  # Para emails de erro do servidor

# URL do site (para links nos emails)
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")
SITE_NAME = "Tucupi Labs"

# Timeout para conexões SMTP (em segundos)
EMAIL_TIMEOUT = 30
