from itertools import chain
from operator import attrgetter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from .constants import ADS_PER_PROFILE_PAGE


class ProfileAdsBase(LoginRequiredMixin, ListView):
    """Base class for user profile ads list pages."""

    template_name = "user_profile/user_ads/my_ads.html"
    paginate_by = ADS_PER_PROFILE_PAGE
    active = True

    # ToDo: move to the service layer
    def get_active_user_ads(self):
        return (
            self.request.user.lost_ads.select_related("type").filter(active=True, open=True),
            self.request.user.found_ads.select_related("type").filter(active=True, open=True),
        )

    def get_inactive_user_ads(self):
        return (
            self.request.user.lost_ads.select_related("type").filter(
                Q(active=False) | Q(open=False)
            ),
            self.request.user.found_ads.select_related("type").filter(
                Q(active=False) | Q(open=False)
            ),
        )

    def get_mixed_ads(self):
        to_mix = self.get_active_user_ads()
        to_count = self.get_inactive_user_ads()
        if not self.active:
            to_mix, to_count = to_count, to_mix

        ads_mix = sorted(chain(*to_mix), key=attrgetter("pub_date"), reverse=True)

        if self.active:
            self.active_count = len(ads_mix)
            self.inactive_count = sum([q.count() for q in to_count])
        else:
            self.inactive_count = len(ads_mix)
            self.active_count = sum([q.count() for q in to_count])

        return ads_mix

    def get_queryset(self):
        return self.get_mixed_ads()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_count"] = self.active_count
        context["inactive_count"] = self.inactive_count
        return context


class ProfileActiveList(ProfileAdsBase):
    """View for active ads page of user profile."""

    active = True


class ProfileInactiveList(ProfileAdsBase):
    """Views for inactive ads page of user profile."""

    active = False
