import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

SILENCED_SYSTEM_CHECKS = []

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", default=get_random_secret_key())
DEBUG = int(os.getenv("DJANGO_DEBUG", default=0))
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="*").split()
LOCAL = int(os.getenv("LOCAL", default=0))

CSRF_FAILURE_VIEW = "core.views.csrf_failure"
if not LOCAL:
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        f"https://*.{os.getenv('WEBSITE_HOST', default='127.0.0.1')}"
    ]

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "ads:index"
# LOGOUT_REDIRECT_URL = 'posts:index'

PHONENUMBER_DEFAULT_REGION = "RU"

AUTH_USER_MODEL = "users.User"

ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_OPEN = True

EMAIL_FILE_PATH = BASE_DIR / "sent_emails"


EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.filebased.EmailBackend"
    if LOCAL
    else "django.core.mail.backends.smtp.EmailBackend",
)

DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER", default="no-reply@pet-alert.ru")
EMAIL_HOST = os.getenv("EMAIL_HOST", default="localhost")
EMAIL_USE_TLS = int(os.getenv("EMAIL_USE_TLS", default=0))
EMAIL_PORT = os.getenv("EMAIL_PORT", default=465)
EMAIL_USE_SSL = int(os.getenv("EMAIL_USE_SSL", default=1))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", default="no-reply@pet-alert.ru")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", default="123123")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ads.apps.AdsConfig",
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "sorl.thumbnail",
    "django_filters",
    "phonenumber_field",
    "django_registration",
    "captcha",
    "rest_framework",
    "djoser",
    "debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = "pet_alert.urls"

TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.year.year",
                "core.context_processors.new_messages.new_messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pet_alert.wsgi.application"

if LOCAL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
            "NAME": os.getenv("DB_NAME", default="postgres"),
            "USER": os.getenv("POSTGRES_USER", default="postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="postgres"),
            "HOST": os.getenv("DB_HOST", default="db"),
            "PORT": os.getenv("DB_PORT", default="5432"),
        }
    }

LOG_PATH = BASE_DIR.parent / ".data" / os.getenv("LOG_DIR", "logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_PATH / "backend.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")
LOG_FORMAT = "[%(asctime)s,%(msecs)d] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
LOG_DT_FORMAT = "%d.%m.%y %H:%M:%S"

LOGGING = {
    "version": 1,
    "disable_exising_loggers": False,
    "formatters": {
        "general": {
            "format": LOG_FORMAT,
            "datefmt": LOG_DT_FORMAT,
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "general",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "interval": 1,
            "backupCount": 14,
            "level": LOG_LEVEL,
            "filename": LOG_PATH,
            "formatter": "general",
        },
    },
    "loggers": {"django": {"level": LOG_LEVEL, "handlers": ["console", "file"]}},
}


if "test" in sys.argv:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
    SILENCED_SYSTEM_CHECKS.append("captcha.recaptcha_test_key_error")
    LOGGING = {}
else:
    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY")
    RECAPTCHA_REQUIRED_SCORE = float(os.getenv("RECAPTCHA_REQUIRED_SCORE", default=0.6))


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"


TIME_ZONE = os.getenv("TIMEZONE", default="Europe/Moscow")

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
if LOCAL:
    STATICFILES_DIRS = ((BASE_DIR / "static"),)
else:
    STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

ANIMAL_ICONS_PATH = "main/img/animal-icons"
ANIMAL_DEFAULT_IMG_PATH = "main/img/default-images"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "PAGE_SIZE": 10,
}

SILENCED_SYSTEM_CHECKS.append("rest_framework.W001")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": True,
}

YA_MAPS_API_KEY = os.getenv("YA_MAPS_API_KEY")
YA_MAPS_SUGGEST_API_KEY = os.getenv("YA_MAPS_SUGGEST_API_KEY")
