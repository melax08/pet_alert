import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from channels.auth import AuthMiddlewareStack  # noqa
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from django.core.asgi import get_asgi_application  # noqa

from server.apps.user_profile.messenger import routing as dialog_routing  # noqa

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(dialog_routing.websocket_urlpatterns)),
    }
)
