import json
from http import HTTPStatus
from itertools import chain
from operator import attrgetter

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, OuterRef, Q, Subquery
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, View
from django.views.generic.base import TemplateView
from django_registration import signals
from django_registration.backends.activation.views import RegistrationView
from users.forms import CreationFormWithoutPassword

from .constants import ADS_PER_PAGE, DIALOGS_PER_PAGE
from .exceptions import BadRequest
from .filters import TypeFilter
from .forms import (
    AuthorizedFoundForm,
    AuthorizedLostForm,
    FoundForm,
    LostForm,
    ProfileSettingsForm,
    SendMessageForm,
)
from .models import Dialog, Found, Lost, Message

REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")

EMAIL_BODY_TEMPLATE = "users/activation_email_body.txt"
EMAIL_SUBJECT_TEMPLATE = "users/activation_email_subject.txt"


User = get_user_model()


class IndexPage(TemplateView):
    """Main page with some information about project."""

    template_name = "ads/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["founds"] = Found.objects.select_related("type").filter(
            active=True, open=True
        )[:4]
        context["losts"] = Lost.objects.select_related("type").filter(
            active=True, open=True
        )[:4]

        return context


class CreateLostAdvertisement(RegistrationView):
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
            signals.user_registered.send(
                sender=self.__class__, user=new_user, request=self.request
            )
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
        return self.render_to_response(
            self.get_context_data(reg_form=reg_form, ad_form=ad_form)
        )

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


class CreateFoundAdvertisement(CreateLostAdvertisement):
    """Just like the CreateLostAdvertisement but for Found advertisements."""

    template_name = "ads/add_found.html"
    ad_with_reg_form_class = FoundForm
    ad_without_reg_form_class = AuthorizedFoundForm


class CreateAdSuccess(TemplateView):
    """Show success page after create new advertisement for authorized user."""

    template_name = "ads/add_success.html"


class CreateAdWithRegSuccess(TemplateView):
    """Show success page after create new advertisement for guest user
    with information about registration on site."""

    template_name = "ads/add_success_reg.html"


class LostList(ListView):
    """Lost list advertisements page."""

    template_name = "ads/lost.html"
    model = Lost
    allow_empty = True
    paginate_by = ADS_PER_PAGE
    filterset_class = TypeFilter

    def get_queryset(self):
        """Creates filterset by filterset_class,
        returns the resulting queryset."""
        queryset = self.model.objects.select_related("type").filter(
            active=True, open=True
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        """Adds additional GET parameters and filter instance to context."""
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        context["parameters"] = get_copy.pop("page", True) and get_copy.urlencode()
        context["filter"] = self.filterset
        return context


class FoundList(LostList):
    """Found list advertisements page."""

    template_name = "ads/found.html"
    model = Found


class LostMap(TemplateView):
    """Lost advertisements map page."""

    template_name = "ads/map.html"
    model = Lost
    ad_model = "l"
    template_title = "Потерялись"

    def _get_advertisements_queryset(self):
        return self.model.objects.prefetch_related("type").filter(
            active=True, open=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = TypeFilter(
            self.request.GET, queryset=self._get_advertisements_queryset()
        )
        context["ad_model"] = self.ad_model
        context["title"] = self.template_title
        return context


class FoundMap(LostMap):
    """Found advertisements map page."""

    model = Found
    ad_model = "f"
    template_title = "Нашлись"


class BaseDetail(DetailView):
    """
    Base class for detail ad pages.
    Only for inheritance.
    """

    template_name = "ads/ad_detail.html"
    context_object_name = "ad"
    pk_url_kwarg = "ad_id"

    def check_access(self):
        """Only opening and active ads are available on the site.
        The user can see their ads even if they are closed."""
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
        return self.model.objects.select_related("author", "type")


class LostDetail(BaseDetail):
    """Lost detail ad page."""

    model = Lost

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ad_title"] = f"Потерялся | {self.object.pet_name}"
        context["ad_model"] = "l"
        context["age_label"] = "Возраст"
        context["balloon_content"] = f"Здесь был {self.object.pet_name}"
        context["author_label"] = "Кто ищет"
        return context


class FoundDetail(BaseDetail):
    """Found detail ad page."""

    model = Found

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ad_title"] = f"Нашелся | {self.object.type.name}"
        context["ad_model"] = "f"
        context["age_label"] = "Примерный возраст"
        context["balloon_content"] = "Был найден тут"
        context["author_label"] = "Кто видел"
        return context


class ProfileAdsBase(LoginRequiredMixin, ListView):
    """Base class for user profile ads list pages."""

    template_name = "ads/my_ads.html"
    paginate_by = ADS_PER_PAGE
    active = True

    def get_active_user_ads(self):
        return (
            self.request.user.lost_ads.select_related("type").filter(
                active=True, open=True
            ),
            self.request.user.found_ads.select_related("type").filter(
                active=True, open=True
            ),
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


class Profile(LoginRequiredMixin, UpdateView):
    """Show the current user settings and allow to edit some of them."""

    template_name = "ads/profile.html"
    form_class = ProfileSettingsForm

    def get_object(self, queryset=None):
        """Set the current request user as instance of form."""
        return self.request.user

    def get_success_url(self):
        """Return user to profile settings page with additional query param."""
        return reverse("ads:profile") + "?success=1"


class DialogList(LoginRequiredMixin, ListView):
    """Shows the list of available chats."""

    template_name = "ads/messages/messages_list.html"
    model = Dialog
    allow_empty = True
    paginate_by = DIALOGS_PER_PAGE
    context_object_name = "chats"

    def get_queryset(self):
        latest_message_pubdate = (
            Message.objects.filter(dialog=OuterRef("pk"))
            .order_by("-pub_date")
            .values("pub_date")[:1]
        )

        latest_message_content = (
            Message.objects.filter(dialog=OuterRef("pk"))
            .order_by("-pub_date")
            .values("content")[:1]
        )

        chats = (
            Dialog.objects.select_related(
                "author",
                "questioner",
                "advertisement_lost",
                "advertisement_found",
                "advertisement_lost__type",
                "advertisement_found__type",
            )
            .filter(Q(author=self.request.user) | Q(questioner=self.request.user))
            .annotate(
                latest_message_date=Subquery(latest_message_pubdate),
                latest_message_content=Subquery(latest_message_content),
                unread_messages=Count(
                    "messages",
                    filter=Q(
                        messages__recipient=self.request.user, messages__checked=False
                    ),
                ),
            )
            .order_by("-latest_message_date")
        )

        return chats


class MessageChat(LoginRequiredMixin, View):
    def get_dialog(self, request):
        dialog = get_object_or_404(
            Dialog.objects.select_related(
                "author",
                "questioner",
                "advertisement_lost__author",
                "advertisement_found__author",
                "advertisement_lost__type",
                "advertisement_found__type",
            ),
            pk=self.kwargs["dialog_id"],
        )

        if not (dialog.author == request.user or dialog.questioner == request.user):
            raise Http404

        return dialog

    def get(self, request, *args, **kwargs):
        dialog = self.get_dialog(request)

        dialog.messages.filter(recipient=self.request.user, checked=False).update(
            checked=True
        )

        form = SendMessageForm()
        messages = dialog.messages.prefetch_related("sender", "recipient").order_by(
            "pub_date"
        )

        return render(
            request,
            "ads/messages/messages_chat.html",
            {
                "messages": messages,
                "form": form,
                "advertisement": dialog.advertisement_group,
            },
        )

    def post(self, request, *args, **kwargs):
        dialog = self.get_dialog(request)

        form = SendMessageForm(request.POST or None)
        if form.is_valid():
            message = form.save(commit=False)
            message.dialog = dialog
            message.sender = request.user
            message.recipient = (
                dialog.author if dialog.author != request.user else dialog.questioner
            )
            message.save()

        return redirect("ads:messages_chat", self.kwargs["dialog_id"])


class FetchBase(View):
    """Class with base functions for fetch requests."""

    MODELS = {"l": Lost, "f": Found}

    @staticmethod
    def _get_request_data(request):
        return json.loads(request.body.decode())

    def _get_model(self, ad_type):
        try:
            model = self.MODELS[ad_type]
        except KeyError:
            raise BadRequest

        return model

    def _get_advertisement(self, request):
        request_body = self._get_request_data(request)
        model = self._get_model(request_body.get("m"))
        ad_id = request_body.get("ad_id")

        try:
            ad = model.objects.get(pk=ad_id)
        except model.DoesNotExist:
            raise BadRequest

        return ad


class AuthFetchBase(LoginRequiredMixin, FetchBase):
    """Fetch base class with LoginRequiredMixin."""

    pass


class GetContactInfo(AuthFetchBase):
    """Processes fetch-request from ads detail page,
    sends author contact information."""

    def post(self, request):
        try:
            ad = self._get_advertisement(request)
            if not ad.active and ad.author != request.user:
                raise BadRequest
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        email, phone = "", ""

        if ad.author.contact_email:
            email = str(ad.author.email)

        if ad.author.contact_phone:
            phone = str(ad.author.phone)

        data = {"email": email, "phone": phone}
        return JsonResponse(data, status=HTTPStatus.OK)


class OpenAd(AuthFetchBase):
    """
    Service view for processing fetch requests from detail post page.
    Allows user to open his advertisement.
    """

    to_set = True

    def post(self, request):
        try:
            ad = self._get_advertisement(request)
            if ad.author != request.user:
                raise BadRequest
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        ad.open = self.to_set
        ad.save()
        return JsonResponse({"message": "success"}, status=HTTPStatus.OK)


class CloseAd(OpenAd):
    """
    Service view for processing fetch requests from detail post page.
    Allows user to close his advertisement.
    """

    to_set = False


class DialogBase(AuthFetchBase):
    """Base class for dialog views."""

    @staticmethod
    def _get_dialog_ad_field(ad):
        if isinstance(ad, Lost):
            return "advertisement_lost"
        return "advertisement_found"


class GetDialog(DialogBase):
    """Fetch view for gets dialog if its exists."""

    def post(self, request):
        try:
            ad = self._get_advertisement(request)
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        try:
            dialog = Dialog.objects.get(
                author=ad.author,
                questioner=request.user,
                **{self._get_dialog_ad_field(ad): ad},
            )
            dialog_id = dialog.id
        except Dialog.DoesNotExist:
            dialog_id = None

        return JsonResponse({"dialog_id": dialog_id})


class CreateDialog(DialogBase):
    """Fetch view for create dialog when the first message sent."""

    def post(self, request):
        message = json.loads(request.body.decode()).get("msg").strip()
        if not message:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        try:
            ad = self._get_advertisement(request)
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        params = {self._get_dialog_ad_field(ad): ad}

        if Dialog.objects.filter(
            author=ad.author, questioner=request.user, **params
        ).exists():
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        dialog = Dialog.objects.create(
            author=ad.author, questioner=request.user, **params
        )
        Message.objects.create(
            dialog=dialog, sender=request.user, recipient=ad.author, content=message
        )
        return JsonResponse({"dialog_id": dialog.id})


class GetAdsBound(FetchBase):
    """Return advertisements within the specified boundaries."""

    def post(self, request):
        request_data = self._get_request_data(request)

        try:
            model = self._get_model(request_data["model"])
            min_x, min_y = request_data["coords"][0]
            max_x, max_y = request_data["coords"][1]
            animal_type = request_data["animal_type"]

            additional_params = dict()
            if animal_type:
                additional_params["type__slug"] = animal_type

            advertisements = model.objects.prefetch_related("type").filter(
                active=True,
                open=True,
                latitude__gte=min_x,
                latitude__lte=max_x,
                longitude__gte=min_y,
                longitude__lte=max_y,
                **additional_params,
            )

            data = [ad.get_map_dict() for ad in advertisements]
            return JsonResponse(data, safe=False)

        except (KeyError, IndexError, BadRequest):
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)
