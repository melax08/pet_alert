from django.urls import include, path

from server.apps.ads.api import urls as api_urls

from . import views

app_name = "ads"

urlpatterns = [
    path("", views.IndexPageView.as_view(), name="index"),
    path("add/found/", views.CreateFoundAdvertisementView.as_view(), name="add_found"),
    path("add/lost/", views.CreateLostAdvertisementView.as_view(), name="add_lost"),
    path("add/success/", views.CreateAdvertisementSuccessView.as_view(), name="add_success"),
    path(
        "add/success-reg/",
        views.CreateAdvertisementRegistrationSuccessView.as_view(),
        name="add_success_reg",
    ),
    path("advertisements/", views.AdvertisementListView.as_view(), name="advertisement_list"),
    path("advertisements/map/", views.AdvertisementMapView.as_view(), name="advertisement_map"),
    path(
        "advertisements/<int:ad_id>/",
        views.AdvertisementDetailView.as_view(),
        name="advertisement_detail",
    ),
    path("api/", include(api_urls)),
]
