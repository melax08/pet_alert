import sys

from decouple import Choices
from django.utils.translation import gettext_lazy as _

from server.settings.components import BASE_DIR, config

SECRET_KEY = config("DJANGO_SECRET_KEY")
DJANGO_ENV = config(
    "DJANGO_ENV", default="development", cast=Choices(["development", "production"])
)

# Application definition:

INSTALLED_APPS = [
    "corsheaders",
    # Project apps:
    "server.apps.ads.apps.AdsConfig",
    "server.apps.core.apps.CoreConfig",
    "server.apps.users.apps.UsersConfig",
    "server.apps.user_profile.apps.UserProfileConfig",
    "server.apps.user_profile.messenger.apps.MessengerConfig",
    # "server.apps.api.apps.ApiConfig",
    # Default Django apps:
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Celery:
    "django_celery_results",
    # Batteries:
    "sorl.thumbnail",
    "django_filters",
    "phonenumber_field",
    "django_registration",
    "django_recaptcha",
    # DRF:
    "rest_framework",
    "djoser",
]

MIDDLEWARE = [
    # Logging:
    "server.settings.components.logging.LoggingContextVarsMiddleware",
    # Content Security Policy:
    "csp.middleware.CSPMiddleware",
    # Cors:
    "corsheaders.middleware.CorsMiddleware",
    # Django:
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Django HTTP Referrer Policy:
    "django_http_referrer_policy.middleware.ReferrerPolicyMiddleware",
]

ROOT_URLCONF = "server.urls"

WSGI_APPLICATION = "server.wsgi.application"

# Database:

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("DJANGO_DATABASE_HOST"),
        "PORT": config("DJANGO_DATABASE_PORT", cast=int),
        "CONN_MAX_AGE": config("CONN_MAX_AGE", cast=int, default=60),
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=300000ms",
        },
    },
}

# Internationalization:

LANGUAGE_CODE = "ru-RU"

USE_I18N = True

USE_L10N = True

LANGUAGES = (
    ("en", _("English")),
    ("ru", _("Russian")),
)

LOCALE_PATHS = ("locale/",)

USE_TZ = True
TIME_ZONE = config("TZ", default="Europe/Moscow")

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"

# Media files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("server", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "server.apps.core.context_processors.year.year",
                "server.apps.core.context_processors.new_messages.new_messages",
            ],
        },
    },
]

# Security

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = "DENY"

# https://github.com/DmytroLitvinov/django-http-referrer-policy
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
REFERRER_POLICY = "same-origin"

# https://github.com/adamchainz/django-permissions-policy#setting
PERMISSIONS_POLICY: dict[str, str | list[str]] = {}  # noqa: WPS234

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]

if "test" in sys.argv:
    SILENCED_SYSTEM_CHECKS.append("django_recaptcha.recaptcha_test_key_error")
    # LOGGING = {}
else:
    RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY")
    RECAPTCHA_REQUIRED_SCORE = config("RECAPTCHA_REQUIRED_SCORE", default=0.6, cast=float)

CSRF_FAILURE_VIEW = "server.apps.core.views.csrf_failure"

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "ads:index"
# LOGOUT_REDIRECT_URL = 'posts:index'

AUTH_USER_MODEL = "users.User"

PHONENUMBER_DEFAULT_REGION = "RU"

ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_OPEN = True

ANIMAL_ICONS_PATH = "main/img/animal-icons"
ANIMAL_DEFAULT_IMG_PATH = "main/img/default-images"
