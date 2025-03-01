from django.urls import path

from . import views

app_name = "ads"

urlpatterns = [
    path("", views.IndexPage.as_view(), name="index"),
    path("add/found/", views.CreateFoundAdvertisement.as_view(), name="add_found"),
    path("add/lost/", views.CreateLostAdvertisement.as_view(), name="add_lost"),
    path("add/success/", views.CreateAdSuccess.as_view(), name="add_success"),
    path(
        "add/success-reg/",
        views.CreateAdWithRegSuccess.as_view(),
        name="add_success_reg",
    ),
    path("lost/list/", views.LostList.as_view(), name="lost"),
    path("lost/map/", views.LostMap.as_view(), name="lost_map"),
    path("lost/<int:ad_id>/", views.LostDetail.as_view(), name="lost_detail"),
    path("found/list/", views.FoundList.as_view(), name="found"),
    path("found/<int:ad_id>/", views.FoundDetail.as_view(), name="found_detail"),
    path("found/map/", views.FoundMap.as_view(), name="found_map"),
    path("profile/", views.Profile.as_view(), name="profile"),
    path("profile/active/", views.ProfileActiveList.as_view(), name="my_ads"),
    path("profile/inactive/", views.ProfileInactiveList.as_view(), name="my_ads_inactive"),
    path(
        "service/contact-info/",
        views.GetContactInfo.as_view(),
        name="get_contact_information",
    ),
    path("service/post-manage/c/", views.CloseAd.as_view(), name="close_ad"),
    path("service/post-manage/o/", views.OpenAd.as_view(), name="open_ad"),
    path("service/get-dialog/", views.GetDialog.as_view(), name="get_dialog"),
    path("service/create-dialog/", views.CreateDialog.as_view(), name="create_dialog"),
    path("profile/messages/", views.DialogList.as_view(), name="messages"),
    path(
        "profile/messages/<int:dialog_id>/",
        views.MessageChat.as_view(),
        name="messages_chat",
    ),
    path("service/coords/", views.GetAdsBound.as_view(), name="coords"),
]
