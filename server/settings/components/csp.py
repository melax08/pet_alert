"""
This file contains a definition for Content-Security-Policy headers.

Read more about it:
https://developer.mozilla.org/ru/docs/Web/HTTP/Headers/Content-Security-Policy

We are using `django-csp` to provide these headers.
Docs: https://github.com/mozilla/django-csp
"""

# These values might and will be redefined in `development.py` env:
CSP_SCRIPT_SRC: tuple[str, ...] = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC: tuple[str, ...] = ("'self'", "data:")
CSP_FONT_SRC: tuple[str, ...] = ("'self'", "fonts.gstatic.com", "fonts.googleapis.com")
CSP_STYLE_SRC: tuple[str, ...] = ("'self'", "'unsafe-inline'", "fonts.googleapis.com")
CSP_DEFAULT_SRC: tuple[str, ...] = ("'self'", "'unsafe-inline'")
CSP_CONNECT_SRC: tuple[str, ...] = ("'self'",)
CSP_FRAME_SRC: tuple[str, ...] = ("'self'",)

# Yandex maps
CSP_SCRIPT_SRC += ("yastatic.net", "api-maps.yandex.ru")
CSP_IMG_SRC += ("*.maps.yandex.net", "api-maps.yandex.ru")

# Google (ReCaptcha)
CSP_SCRIPT_SRC += ("www.google.com", "www.gstatic.com")
CSP_FRAME_SRC += ("www.google.com",)

# Messenger styles
CSP_STYLE_SRC += ("maxcdn.bootstrapcdn.com",)
CSP_FONT_SRC += ("maxcdn.bootstrapcdn.com",)
