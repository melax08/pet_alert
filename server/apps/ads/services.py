from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from server.apps.users.models import User

from .choices import AdType
from .models import AdsAbstract, Found, Lost

ad_type_literal_model_mapping: dict[AdType, type[AdsAbstract]] = {
    AdType.LOST: Lost,
    AdType.FOUND: Found,
}


class AdvertisementService:
    @staticmethod
    def get_ad_model_by_ad_type(ad_type: AdType) -> type[AdsAbstract] | None:
        try:
            return ad_type_literal_model_mapping[ad_type]
        except KeyError:
            return None

    @staticmethod
    def get_active_advertisement_queryset(model: type[AdsAbstract]) -> QuerySet[type[AdsAbstract]]:
        return model.objects.filter(open=True, active=True)

    def get_advertisement_or_404(self, ad_type: AdType, ad_id: int) -> type[AdsAbstract] | None:
        advertisement_model = self.get_ad_model_by_ad_type(ad_type=ad_type)
        return get_object_or_404(
            self.get_active_advertisement_queryset(advertisement_model),
            id=ad_id,
        )

    @staticmethod
    def is_user_advertisement_author(advertisement: type[AdsAbstract], user: User) -> bool:
        return advertisement.author == user
