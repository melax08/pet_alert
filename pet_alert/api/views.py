from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from ads.models import AnimalType, Lost, Found  # noqa
from .serializers import (
    AnimalTypeSerializer,
    LostAdSerializer,
    FoundAdSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly


class AnimalTypeViewSet(ModelViewSet):
    """View set to manage AnimalType model."""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class LostAdViewSet(ModelViewSet):
    """View set to manage Lost ads."""
    queryset = Lost.objects.all()
    serializer_class = LostAdSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('type',)  # ToDo: сделать возможность фильтрации по type__slug.

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ('partial_update', 'update', 'destroy'):
            return IsAdminOrReadOnly(),
        return super().get_permissions()

    def _open_processing(self, request, to_set: bool, error_message: str):
        ad = self.get_object()
        if ad.author != request.user and not request.user.is_staff:
            return Response({'errors': 'Доступ запрещен'},
                            status=status.HTTP_403_FORBIDDEN)
        if ad.open == to_set:
            raise serializers.ValidationError(
                {'detail': error_message}
            )

        ad.open = to_set
        ad.save()
        return Response(
            self.get_serializer(ad, many=False).data,
            status=status.HTTP_200_OK
        )

    def _activation_processing(self, to_set: bool, error_message: str):
        ad = self.get_object()
        if ad.active == to_set:
            raise serializers.ValidationError(
                {'detail': error_message}
            )
        ad.active = to_set
        ad.save()
        return Response(
            self.get_serializer(ad, many=False).data,
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=True)
    def open(self, request, *args, **kwargs):
        return self._open_processing(request, True, 'Объявление уже открыто')

    @action(methods=['post'], detail=True)
    def close(self, request, *args, **kwargs):
        return self._open_processing(request, False, 'Объявление уже закрыто')

    @action(methods=['post'], detail=True,
            permission_classes=(IsAdminOrReadOnly,))
    def activate(self, request, *args, **kwargs):
        return self._activation_processing(True, 'Объявление уже активно')

    @action(methods=['post'], detail=True,
            permission_classes=(IsAdminOrReadOnly,))
    def deactivate(self, request, *args, **kwargs):
        return self._activation_processing(
            False, 'Объявление уже деактивировано'
        )


class FoundAdViewSet(LostAdViewSet):
    queryset = Found.objects.all()
    serializer_class = FoundAdSerializer
