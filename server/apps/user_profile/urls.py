from django.urls import path

from . import views

app_name = "user_profile"

urlpatterns = [
    path("settings/", views.UserProfileSettingsView.as_view(), name="settings"),
]
