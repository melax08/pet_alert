from django.urls import path

from . import views

app_name = "messenger"

urlpatterns = [
    path("service/get-dialog/", views.GetDialog.as_view(), name="get_dialog"),
    path("service/create-dialog/", views.CreateDialog.as_view(), name="create_dialog"),
    path("profile/messenger/", views.DialogList.as_view(), name="messages"),
    path("profile/messenger/<int:dialog_id>/", views.MessageChat.as_view(), name="messages_chat"),
]
