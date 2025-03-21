from itertools import chain
from operator import attrgetter

from django.db.models import Q, QuerySet

from server.apps.ads.models import Found, Lost
from server.apps.users.models import User


class UserAdsService:
    def __init__(self, user: User) -> None:
        self.user = user

    def get_active_user_ads(self) -> tuple[QuerySet[Lost], QuerySet[Found]]:
        """Get all active user advertisements from lost and found."""
        return (
            self.user.lost_ads.select_related("type").filter(active=True, open=True),
            self.user.found_ads.select_related("type").filter(active=True, open=True),
        )

    def get_inactive_user_ads(self) -> tuple[QuerySet[Lost], QuerySet[Found]]:
        """
        Get all inactive user advertisements from lost and found.
        An inactive ad is one that has not passed moderation or has been disabled by the user.
        """
        return (
            self.user.lost_ads.select_related("type").filter(Q(active=False) | Q(open=False)),
            self.user.found_ads.select_related("type").filter(Q(active=False) | Q(open=False)),
        )

    def get_mixed_ads(self, is_active: bool) -> tuple[list[Lost | Found], int, int]:
        """Mix active or inactive ads in one list and count amount of active and inactive ads."""
        to_mix = self.get_active_user_ads()
        to_count = self.get_inactive_user_ads()
        if not is_active:
            to_mix, to_count = to_count, to_mix

        ads_mix = sorted(chain(*to_mix), key=attrgetter("pub_date"), reverse=True)

        if is_active:
            active_count = len(ads_mix)
            inactive_count = sum([q.count() for q in to_count])
        else:
            inactive_count = len(ads_mix)
            active_count = sum([q.count() for q in to_count])

        return ads_mix, active_count, inactive_count
