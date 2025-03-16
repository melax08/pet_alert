from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView

from .forms import ProfileSettingsForm


class UserProfileSettingsView(LoginRequiredMixin, UpdateView):
    """Show the current user settings and allow to edit some of them."""

    template_name = "user_profile/settings.html"
    form_class = ProfileSettingsForm

    def get_object(self, queryset=None):
        """Set the current request user as instance of form."""
        return self.request.user

    def get_success_url(self):
        """Return user to profile settings page with additional query param."""
        return reverse("user_profile:settings") + "?success=1"
