from django.urls import path

from . import views

app_name = "user_ads"

urlpatterns = [
    path("active/", views.ProfileAdsActiveListView.as_view(), name="active"),
    path("inactive/", views.ProfileAdsInactiveListView.as_view(), name="inactive"),
]
