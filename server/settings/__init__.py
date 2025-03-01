from decouple import Choices, config
from split_settings.tools import include

_ENV = config("DJANGO_ENV", default="development", cast=Choices(["development", "production"]))

include(
    "components/common.py",
    "components/email.py",
    "components/caches.py",
    "components/celery.py",
    "components/drf.py",
    "components/logging.py",
    "components/cors.py",
    "components/csp.py",
    "components/sentry.py",
    "components/third_party_apis.py",
    f"environments/{_ENV}.py",
)
