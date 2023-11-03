from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from ads.models import AnimalType, Lost, Found  # noqa
from .serializers import (
    AnimalTypeSerializer,
    LostAdListSerializer,
    FoundAdListSerializer,
    LostAdDetailSerializer,
    FoundAdDetailSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .filters import AdFilter


class AnimalTypeViewSet(ModelViewSet):
    """View set to manage AnimalType model."""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class LostAdViewSet(ModelViewSet):
    """View set to manage Lost ads."""
    model = Lost
    serializer_class = LostAdListSerializer
    detail_serializer_class = LostAdDetailSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """
        - Admin can work with all model objects.
        - Authenticated user can work with active, open and own objects.
        - Anonymous can work with open and active objects.
        """
        if self.request.user.is_staff:
            return self.model.objects.select_related('type', 'author').all()

        if (self.request.user.is_authenticated
                and self.action in ('retrieve', 'open', 'close')):
            return self.model.objects.select_related('type', 'author').filter(
                Q(active=True, open=True) | Q(author=self.request.user))

        return self.model.objects.select_related('type', 'author').filter(
            active=True, open=True)

    def perform_create(self, serializer):
        """Set the author of created ad to the request user."""
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ('partial_update', 'update', 'destroy'):
            return IsAdminOrReadOnly(),
        return super().get_permissions()

    def get_serializer_class(self):
        """Detail GET, PATCH, PUT and management requests use special
        serializer."""
        if self.action in (
                'retrieve',
                'partial_update',
                'update',
                'open',
                'close',
                'activate',
                'deactivate'
        ):
            return self.detail_serializer_class

        return self.serializer_class

    def _open_processing(self, request, to_set: bool, error_message: str):
        """
        Open or close the advertisement.
        Only author of advertisement or admin can make this action.
        """
        ad = self.get_object()
        if ad.author != request.user and not request.user.is_staff:
            raise PermissionDenied({'errors': 'Доступ запрещен'})

        if ad.open is to_set:
            raise serializers.ValidationError({'detail': error_message})

        ad.open = to_set
        ad.save()
        return Response(
            self.get_serializer(ad, many=False).data,
            status=status.HTTP_200_OK
        )

    def _activation_processing(self, to_set: bool, error_message: str):
        """Activate or deactivate the advertisement."""
        ad = self.get_object()

        if ad.active is to_set:
            raise serializers.ValidationError({'detail': error_message})

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
        return self._activation_processing(False, 'Объявление уже неактивно')


class FoundAdViewSet(LostAdViewSet):
    """View set to manage Found ads."""
    model = Found
    serializer_class = FoundAdListSerializer
    detail_serializer_class = FoundAdDetailSerializer
