from rest_framework.viewsets import ModelViewSet

from ads.models import AnimalType  # noqa
from .serializers import AnimalTypeSerializer
from .permissions import IsAdminOrReadOnly


class AnimalTypeViewSet(ModelViewSet):
    """View set to manage AnimalType model."""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
