from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()

router.register(r"animal-type", views.AnimalTypeViewSet, basename="animal_type")
router.register(r"lost", views.LostAdViewSet, basename="lost")
router.register(r"found", views.FoundAdViewSet, basename="found")

urlpatterns = [
    path("", include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path("auth/", include("djoser.urls.jwt")),
]
