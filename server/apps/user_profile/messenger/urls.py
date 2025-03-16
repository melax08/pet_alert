from django.urls import path

from server.apps.user_profile.messenger.api.views import CreateDialogView, GetDialogView

from . import views

app_name = "messenger"

urlpatterns = [
    path("api/get-dialog/", GetDialogView.as_view(), name="get_dialog"),
    path("api/create-dialog/", CreateDialogView.as_view(), name="create_dialog"),
    path("", views.MessengerDialogListView.as_view(), name="dialog_list"),
    path("<int:dialog_id>/", views.MessengerDialogDetailView.as_view(), name="dialog_detail"),
]
