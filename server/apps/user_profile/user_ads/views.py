from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .constants import ADS_PER_PROFILE_PAGE
from .services import UserAdsService


class ProfileAdsBaseView(LoginRequiredMixin, ListView):
    """Base class for user profile ads list pages."""

    template_name: str = "user_profile/user_ads/my_ads.html"
    paginate_by: int = ADS_PER_PROFILE_PAGE
    is_active: bool

    def get_queryset(self):
        service = UserAdsService(user=self.request.user)
        ads, reverse_count = service.get_ads_list(self.is_active)
        self.reverse_count = reverse_count
        return ads

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.is_active:
            context["active_count"] = context["paginator"].count
            context["inactive_count"] = self.reverse_count
        else:
            context["active_count"] = self.reverse_count
            context["inactive_count"] = context["paginator"].count

        return context


class ProfileAdsActiveListView(ProfileAdsBaseView):
    """View for active ads page of user profile."""

    is_active = True


class ProfileAdsInactiveListView(ProfileAdsBaseView):
    """Views for inactive ads page of user profile."""

    is_active = False
