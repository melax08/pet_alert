from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from server.apps.user_profile import urls as user_profile_urls
from server.apps.user_profile.messenger import urls as messenger_urls

handler404 = "server.apps.core.views.page_not_found"
handler500 = "server.apps.core.views.server_error"
handler403 = "server.apps.core.views.permission_denied"

urlpatterns = [
    path("", include("server.apps.ads.urls", namespace="ads")),
    path("profile/messenger/", include(messenger_urls, namespace="messenger")),
    path("profile/", include(user_profile_urls, namespace="user_profile")),
    path("admin/", admin.site.urls),
    # path('auth/', include('django_registration.backends.activation.urls')),
    path("auth/", include("server.apps.users.urls", namespace="users")),
    path("auth/", include("django.contrib.auth.urls")),
    path("api/v1/", include("server.apps.api.urls", namespace="api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
