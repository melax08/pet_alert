from django.urls import re_path

from server.apps.user_profile.messenger.consumers import DialogConsumer

websocket_urlpatterns = [
    re_path(r"ws/dialog/(?P<dialog_id>\d+)/$", DialogConsumer.as_asgi()),
]
