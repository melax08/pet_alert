from django.urls import path

from .views import (
    CloseAdvertisementView,
    GetContactInfoView,
    MapAdvertisementsView,
    OpenAdvertisementView,
)

urlpatterns = [
    path("get-contact-info/", GetContactInfoView.as_view(), name="get_contact_info"),
    path("open-advertisement/", OpenAdvertisementView.as_view(), name="open_advertisement"),
    path("close-advertisement/", CloseAdvertisementView.as_view(), name="close_advertisement"),
    path("map-coords/", MapAdvertisementsView.as_view(), name="get_coords"),
]
