from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django_registration import signals
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.views import PasswordResetConfirmView

from .forms import CreationForm, CreationFormWithoutPassword
from ads.forms import LostForm, FoundForm



# class SignUp(CreateView):
#     form_class = CreationForm
#     success_url = reverse_lazy('users:confirmation_info')
#     template_name = 'users/signup.html'

# def signup(request):
#     template = 'users/signup.html'
#     form = CreationForm(request.POST or None)
#     if form.is_valid():
#         temp = form.save(commit=False)
#         temp.active = False
#
#
# class ConfirmationInfo(TemplateView):
#     template_name = 'users/confirmation_info.html'

class CustomActivationView(PasswordResetConfirmView):


    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())