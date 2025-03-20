from django.urls import path

from . import views

app_name = "user_ads"

urlpatterns = [
    path("active/", views.ProfileActiveList.as_view(), name="active"),
    path("inactive/", views.ProfileInactiveList.as_view(), name="inactive"),
]
