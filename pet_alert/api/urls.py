from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnimalTypeViewSet

app_name = 'api'

router = DefaultRouter()

router.register(r'animal-type', AnimalTypeViewSet, basename='animal_type')

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]