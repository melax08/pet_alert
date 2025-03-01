from server.settings.components.caches import REDIS_URL
from server.settings.components.common import TIME_ZONE

CELERY_BROKER_URL = REDIS_URL

CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True

CELERY_TIMEZONE = TIME_ZONE
CELERY_DEFAULT_QUEUE = "pet-alert-celery"
