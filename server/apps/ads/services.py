from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from server.apps.users.models import User

from .models import Advertisement, Found, Lost


class AdvertisementService:
    @staticmethod
    def update_context_with_lost_and_found_advertisements(
        context: dict[Any, Any], ads_count: int
    ) -> None:
        context["founds"] = (
            Found.objects.select_related("species")
            .filter(active=True, open=True)
            .values("id", "created_at", "image", "species__default_image")[:ads_count]
        )
        context["losts"] = (
            Lost.objects.select_related("species")
            .filter(active=True, open=True)
            .values("id", "created_at", "image", "species__default_image")[:ads_count]
        )

    @staticmethod
    def get_active_advertisement_queryset() -> QuerySet[Advertisement]:
        return Advertisement.objects.filter(open=True, active=True)

    @staticmethod
    def get_advertisement_or_404(ad_id: int) -> Advertisement:
        return get_object_or_404(Advertisement, id=ad_id)

    def get_visible_advertisement_or_404(self, ad_id: int) -> Advertisement:
        return get_object_or_404(self.get_active_advertisement_queryset(), id=ad_id)

    @staticmethod
    def is_user_advertisement_author(advertisement: type[Advertisement], user: User) -> bool:
        return advertisement.author == user

    @staticmethod
    def get_advertisement_author_contact_info(advertisement: Advertisement) -> dict[str, str]:
        return {
            "email": str(advertisement.author.email) if advertisement.author.contact_email else "",
            "phone": str(advertisement.author.phone) if advertisement.author.contact_phone else "",
        }

    @staticmethod
    def open_advertisement(advertisement: Advertisement) -> None:
        if not advertisement.open:
            advertisement.open = True
            advertisement.save(update_fields=["open"])

    @staticmethod
    def close_advertisement(advertisement: Advertisement) -> None:
        if advertisement.open:
            advertisement.open = False
            advertisement.save(update_fields=["open"])
