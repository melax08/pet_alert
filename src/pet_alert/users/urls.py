from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import RegistrationView

from .forms import (
    CreationForm,
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    CustomResetForm,
    CustomSetPasswordForm,
)
from .views import CustomActivationView

app_name = "users"

urlpatterns = [
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path(
        "signup/",
        RegistrationView.as_view(
            form_class=CreationForm,
            template_name="users/registration_form.html",
            success_url=reverse_lazy("users:signup_complete"),
            disallowed_url=reverse_lazy("users:signup_disallowed"),
            email_subject_template="users/activation_email_subject.txt",
            email_body_template="users/activation_email_body.txt",
        ),
        name="signup",
    ),
    path(
        "activate/complete/",
        TemplateView.as_view(template_name="users/activation_complete.html"),
        name="signup_activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        CustomActivationView.as_view(),
        name="registration_activate",
    ),
    path(
        "signup/complete/",
        TemplateView.as_view(template_name="users/registration_complete.html"),
        name="signup_complete",
    ),
    path(
        "signup/closed/",
        TemplateView.as_view(template_name="users/registration_closed.html"),
        name="signup_disallowed",
    ),
    path(
        "login/",
        LoginView.as_view(
            template_name="users/login.html", form_class=CustomAuthenticationForm
        ),
        name="login",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="users/password_change_form.html",
            form_class=CustomPasswordChangeForm,
        ),
        name="change_form",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="change_done",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html", form_class=CustomResetForm
        ),
        name="reset_form",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
        ),
        name="reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="reset_complete",
    ),
    path(
        "set-password/done",
        TemplateView.as_view(template_name="users/password_set_done.html"),
        name="set_password_done",
    ),
]
