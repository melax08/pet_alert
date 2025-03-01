"""
This file contains all the settings that defines the development server.
"""

import socket
from typing import TYPE_CHECKING

from server.settings.components import BASE_DIR
from server.settings.components.common import (
    DATABASES,
    INSTALLED_APPS,
    MIDDLEWARE,
)
from server.settings.components.csp import CSP_CONNECT_SRC, CSP_IMG_SRC, CSP_SCRIPT_SRC

if TYPE_CHECKING:
    from django.http import HttpRequest

DEBUG = True

# ToDo: check path
STATICFILES_DIRS = ((BASE_DIR / "server/static"),)

ALLOWED_HOSTS = ["*"]  # Allow all hosts in development

INSTALLED_APPS += ("debug_toolbar",)

MIDDLEWARE += (
    # Django debug toolbar:
    # https://django-debug-toolbar.readthedocs.io
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # https://github.com/bradmontgomery/django-querycount
    # Prints how many queries were executed, useful for the APIs.
    "querycount.middleware.QueryCountMiddleware",
)


# ToDo: check is it need?
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html#configure-internal-ips
try:  # This might fail on some OS
    INTERNAL_IPS = [
        "{0}.1".format(ip[: ip.rfind(".")])  # noqa: UP030
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    ]
except OSError:  # pragma: no cover
    INTERNAL_IPS = []

INTERNAL_IPS += ["127.0.0.1", "10.0.2.2"]


def _custom_show_toolbar(request: "HttpRequest") -> bool:
    """Only show the debug toolbar to users with the superuser flag."""
    return DEBUG and request.user.is_superuser


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "server.settings.environments.development._custom_show_toolbar",  # noqa: E501
}

# This will make debug toolbar to work with django-csp,
# since `ddt` loads some scripts from `ajax.googleapis.com`:
CSP_SCRIPT_SRC += ("ajax.googleapis.com",)
CSP_IMG_SRC += ("data:",)
CSP_CONNECT_SRC += ("'self'",)

DATABASES["default"]["CONN_MAX_AGE"] = 0
