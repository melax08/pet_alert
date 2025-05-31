from django.db.models import Q, QuerySet

from server.apps.ads.models import Advertisement
from server.apps.users.models import User


class UserAdsService:
    def __init__(self, user: User) -> None:
        self.user = user

    def get_active_user_ads_qs(self) -> QuerySet[Advertisement]:
        """Get all active user advertisements from lost and found."""
        return (
            self.user.advertisements.select_related("species")
            .filter(active=True, open=True)
            .order_by("-created_at")
        )

    def get_inactive_user_ads_qs(self) -> QuerySet[Advertisement]:
        """
        Get all inactive user advertisements from lost and found.
        An inactive ad is one that has not passed moderation or has been disabled by the user.
        """
        return (
            self.user.advertisements.select_related("species")
            .filter(Q(active=False) | Q(open=False))
            .order_by("-created_at")
        )

    def get_ads_list(self, is_active: bool) -> tuple[QuerySet[Advertisement], int]:
        """Get user active or inactive advertisements with count of active and inactive ads."""
        active_ads = self.get_active_user_ads_qs()
        inactive_ads = self.get_inactive_user_ads_qs()

        ads = active_ads if is_active else inactive_ads
        reverse_count = inactive_ads.count() if is_active else active_ads.count()

        return ads, reverse_count
