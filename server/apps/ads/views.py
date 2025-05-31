from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django_registration import signals
from django_registration.backends.activation.views import RegistrationView

from server.apps.users.forms import CreationFormWithoutPassword

from .constants import ADS_PER_PAGE
from .filters import AdvertisementListFilterSet
from .forms import (
    AuthorizedFoundForm,
    AuthorizedLostForm,
    FoundForm,
    LostForm,
)
from .models import Advertisement, Lost
from .services import AdvertisementService

REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")

EMAIL_BODY_TEMPLATE = "users/activation_email_body.txt"
EMAIL_SUBJECT_TEMPLATE = "users/activation_email_subject.txt"

User = get_user_model()


class IndexPageView(TemplateView):
    """Main page with some information about project and last
    Lost and Found advertisements."""

    template_name = "ads/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AdvertisementService.update_context_with_lost_and_found_advertisements(context, ads_count=4)
        return context


class CreateLostAdvertisementView(RegistrationView):
    """
    - Guest user can create an advertisement.
    - During creating of advertisement, user will be registered
    at site without password.
    - User needs to follow the link on email to proceed the registration.
    - If user already registered and authenticated, he can just create an
    advertisement.
    """

    email_subject_template = "users/activation_email_subject.txt"
    email_body_template = "users/activation_email_body.txt"
    template_name = "ads/add_lost.html"
    registration_form_class = CreationFormWithoutPassword
    ad_with_reg_form_class = LostForm
    ad_without_reg_form_class = AuthorizedLostForm
    disallowed_url = reverse_lazy("users:signup_disallowed")

    def register(self, ad_form, reg_form=None):
        """
        Register a new (inactive) user account, generate an activation key
        and email it to the user, create advertisement
        and set new user the author of it.
        """
        if reg_form:
            new_user = self.create_inactive_user(reg_form)
            signals.user_registered.send(sender=self.__class__, user=new_user, request=self.request)
            author_to_set = new_user
        else:
            author_to_set = self.request.user

        adv_instance = ad_form.save(commit=False)
        adv_instance.author = author_to_set
        adv_instance.save()

        if reg_form:
            return author_to_set

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate the forms instance with the passed
        POST variables and then check if it's valid.
        """
        reg_form = self.get_registration_form()
        ad_form = self.get_form()

        if reg_form and reg_form.errors.get("phone"):
            del reg_form.errors["phone"]

        if ad_form.is_valid() and (reg_form is None or reg_form.is_valid()):
            return self.form_valid(reg_form, ad_form)

        return self.form_invalid(reg_form, ad_form)

    def get_success_url(self, user=None):
        """Return the URL to redirect after successful POST request."""
        if self.request.user.is_authenticated:
            return reverse_lazy("ads:add_success")

        return reverse_lazy("ads:add_success_reg")

    def form_valid(self, reg_form, ad_form):
        """If the forms are valid, register user, create
        post and return success url."""
        return HttpResponseRedirect(
            self.get_success_url(self.register(ad_form=ad_form, reg_form=reg_form))
        )

    def form_invalid(self, reg_form, ad_form):
        """If the forms are invalid, render the invalid forms."""
        return self.render_to_response(self.get_context_data(reg_form=reg_form, ad_form=ad_form))

    def get_form(self, form_class=None):
        """Returns an instance of add advertisement form to be used in this
        view. Deleted check for user_model from RegistrationView."""
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(**self.get_form_kwargs())

    def get_form_class(self):
        """Return a form class depending on whether the user is logged in."""
        if self.request.user.is_authenticated:
            return self.ad_without_reg_form_class

        return self.ad_with_reg_form_class

    def get_registration_form(self):
        """If user is not authenticated return the registration form."""
        if not self.request.user.is_authenticated:
            return self.registration_form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """Insert the forms into the context dict."""
        if "ad_form" not in kwargs:
            kwargs["reg_form"] = self.get_registration_form()
            kwargs["ad_form"] = self.get_form()
        return super().get_context_data(**kwargs)


class CreateFoundAdvertisementView(CreateLostAdvertisementView):
    """Just like the CreateLostAdvertisement but for Found advertisements."""

    template_name = "ads/add_found.html"
    ad_with_reg_form_class = FoundForm
    ad_without_reg_form_class = AuthorizedFoundForm


class CreateAdvertisementSuccessView(TemplateView):
    """Show success page after create new advertisement for authorized user."""

    template_name = "ads/add_success.html"


class CreateAdvertisementRegistrationSuccessView(TemplateView):
    """Show success page after create new advertisement for guest user
    with information about registration on site."""

    template_name = "ads/add_success_reg.html"


class AdvertisementListView(ListView):
    """Advertisements list page."""

    template_name = "ads/advertisement_list.html"
    model = Advertisement
    allow_empty = True
    paginate_by = ADS_PER_PAGE
    filterset_class = AdvertisementListFilterSet

    def get_queryset(self):
        """Creates filterset by filterset_class, returns the resulting queryset."""
        queryset = self.model.objects.select_related("species").filter(active=True, open=True)
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        """Adds additional GET parameters and filter instance to context."""
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        context["parameters"] = get_copy.pop("page", True) and get_copy.urlencode()
        context["filter"] = self.filterset
        return context


class AdvertisementMapView(TemplateView):
    """Advertisements map page."""

    template_name = "ads/advertisement_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = AdvertisementListFilterSet(
            self.request.GET,
            queryset=Advertisement.objects.select_related("species").filter(active=True, open=True),
        )
        return context


class AdvertisementDetailView(DetailView):
    """Advertisements detail page."""

    model = Advertisement
    template_name = "ads/advertisement_detail.html"
    context_object_name = "ad"
    pk_url_kwarg = "ad_id"

    def check_access(self):
        """Only open and active ads are available on the site.
        The user can view his ads even if they are closed."""
        if (
            not (self.object.active and self.object.open)
            and self.object.author != self.request.user
        ):
            raise Http404

    def get(self, request, *args, **kwargs):
        """Add check_access function call after get object."""
        self.object = self.get_object()
        self.check_access()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_queryset(self):
        """Get queryset with join tables author and type."""
        return self.model.objects.select_related("author", "species")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.__class__ is Lost:
            context["ad_title"] = f"Потерялся | {self.object.pet_name}"
            context["ad_model"] = "l"  # ToDo: delete
            context["age_label"] = "Возраст"
            context["balloon_content"] = f"Здесь был {self.object.pet_name}"
            context["author_label"] = "Кто ищет"
        else:
            context["ad_title"] = f"Нашелся | {self.object.species.name}"
            context["ad_model"] = "f"  # ToDo: delete
            context["age_label"] = "Примерный возраст"
            context["balloon_content"] = "Был найден тут"
            context["author_label"] = "Кто видел"

        return context
