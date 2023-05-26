from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core import signing
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordContextMixin
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django_registration import signals

User = get_user_model()

INTERNAL_SET_SESSION_TOKEN = "_password_set_token"
REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")


class CustomActivationView(PasswordContextMixin, FormView):
    """
    Custom activation view-class.
    If user make common registration, he needs to follow the link
    and the account is activated. If user make registration via advertisement,
    he needs to follow the link and set a password for the account,
    after that, the account will be activated.
    """
    success_url = reverse_lazy("users:set_password_done")
    template_name = 'users/password_set_confirm.html'
    form_class = SetPasswordForm
    post_reset_login = True
    post_reset_login_backend = None
    reset_url_token = "set-password"
    title = _("Enter new password")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.validlink = False
        key = kwargs.get('activation_key')
        self.user = self.get_user(key)

        if self.user is None:
            if key == self.reset_url_token:
                session_token = self.request.session.get(
                    INTERNAL_SET_SESSION_TOKEN)
                self.user = self.get_user(session_token)
                if self.user is not None:
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
        else:
            if check_password('', self.user.password):
                self.request.session[INTERNAL_SET_SESSION_TOKEN] = key
                redirect_url = self.request.path.replace(key,
                                                         self.reset_url_token)
                return HttpResponseRedirect(redirect_url)
            else:
                self.user.is_active = True
                signals.user_activated.send(
                    sender=self.__class__, user=self.user, request=self.request
                )
                self.user.save()
                auth_login(self.request, self.user)
                return redirect(reverse_lazy(
                    'users:signup_activation_complete'))

        # Display the "account activation unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, activation_key):
        """Verify that the activation key is valid and within the
        permitted activation time window, then look up and return the
        corresponding user account if it exists, or raising
        ``ActivationError`` if it doesn't."""
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400,
            )
            user = User.objects.get(**{User.USERNAME_FIELD: username})
            if user.is_active:
                user = None
        except (signing.SignatureExpired,
                signing.BadSignature,
                User.DoesNotExist):
            user = None
        return user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )
        user.save()
        del self.request.session[INTERNAL_SET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context
