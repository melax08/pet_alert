# type: ignore
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from server.settings.components import config
from server.settings.components.common import DJANGO_ENV

SENTRY_DSN = config("SENTRY_DSN", default="")

if SENTRY_DSN:
    if DJANGO_ENV == "development":
        traces_sample_rate: float = 1.0
        profiles_sample_rate: float = 1.0
    else:
        traces_sample_rate: float = 0.5
        profiles_sample_rate: float = 0.5

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=True,
    )
