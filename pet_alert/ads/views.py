import json
from http import HTTPStatus
from itertools import chain
from operator import attrgetter

from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from sorl.thumbnail import get_thumbnail
from django_registration import signals
from django.conf import settings
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, OuterRef, Subquery
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, View

from .constants import ADS_PER_PAGE, DESCRIPTION_MAP_LIMIT, DIALOGS_PER_PAGE
from .models import Found, Lost, Message, Dialog
from .forms import (FoundForm, LostForm, AuthorizedFoundForm,
                    AuthorizedLostForm, ChangeNameForm, SendMessageForm)
from .filters import TypeFilter
from .exceptions import BadRequest
from users.forms import CreationForm, CreationFormWithoutPassword  # noqa


REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")

EMAIL_BODY_TEMPLATE = 'users/activation_email_body.txt'
EMAIL_SUBJECT_TEMPLATE = 'users/activation_email_subject.txt'


User = get_user_model()


class IndexPage(TemplateView):
    """Main page with some information about project."""
    template_name = 'ads/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['founds'] = Found.objects.filter(active=True, open=True)[:4]
        context['losts'] = Lost.objects.filter(active=True, open=True)[:4]

        return context


class AdWithRegistration(RegistrationView):
    """
    - Guest user can create an advertisement.
    - During creating of advertisement, user will be registered
    at site without password.
    - User needs to follow the link on email to proceed the registration.
    """
    email_subject_template = 'users/activation_email_subject.txt'
    email_body_template = 'users/activation_email_body.txt'
    template_name = 'ads/add_lost.html'
    form_class = CreationFormWithoutPassword
    success_url = reverse_lazy('ads:add_success_reg')
    disallowed_url = reverse_lazy("users:signup_disallowed")

    def register(self, form, ad_form):
        """
        Register a new (inactive) user account, generate an activation key
        and email it to the user, create advertisement
        and set new user the author of it.
        """
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=self.request
        )
        set_author = ad_form.save(commit=False)
        set_author.author = new_user
        set_author.save()
        return new_user

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate the forms instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        ad_form = self.get_ad_form()
        if form.is_valid() and ad_form.is_valid():
            return self.form_valid(form, ad_form)
        else:
            return self.form_invalid(form, ad_form)

    def form_valid(self, form, ad_form):
        """If the forms are valid, register user, create
        post and return success url."""
        return HttpResponseRedirect(
            self.get_success_url(self.register(form, ad_form)))

    def form_invalid(self, form, ad_form):
        """If the forms are invalid, render the invalid forms."""
        return self.render_to_response(self.get_context_data(form=form,
                                                             ad_form=ad_form))

    def get_form(self, form_class=None):
        """Returns an instance of the form to be used in this view.
        Deleted check for user_model."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_ad_form(self):
        """Returns an instance of the ad form to be used in this view."""
        if self.request.resolver_match.view_name == 'ads:add_lost':
            return LostForm(**self.get_form_kwargs())
        return FoundForm(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """Insert the forms into the context dict."""
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()
            kwargs["ad_form"] = self.get_ad_form()
        return super().get_context_data(**kwargs)


class CreateAdAuthorized(LoginRequiredMixin, CreateView):
    """Base class for create advertisement pages.
    You need to specify template_name and form_class while inheritance."""
    success_url = reverse_lazy('ads:add_success')

    def form_valid(self, form):
        """Save current user as author of advertisement."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict with custom
        template variable name."""
        # ToDo: изменить во вьюхе с добавлением объявления и регистрацией
        #  дефолтное поле для формы объявления с ad_form на просто form
        #  после этого, убрать этот метод
        context = super().get_context_data(**kwargs)
        context["ad_form"] = context["form"]
        context["form"] = None
        return context


def add_found(request):
    """Handler for add found page.
    Authorized user and guest will see different pages."""
    if request.user.is_authenticated:
        return CreateAdAuthorized.as_view(
            template_name='ads/add_found.html',
            form_class=AuthorizedFoundForm
        )(request)
    return AdWithRegistration.as_view(
        template_name='ads/add_found.html'
    )(request)


def add_lost(request):
    """Handler for add lost page.
    Authorized user and guest will see different pages."""
    if request.user.is_authenticated:
        return CreateAdAuthorized.as_view(
            template_name='ads/add_lost.html',
            form_class=AuthorizedLostForm
        )(request)
    return AdWithRegistration.as_view(
        template_name='ads/add_lost.html'
    )(request)


class CreateAdSuccess(TemplateView):
    """Show success page after create new advertisement for authorized user."""
    template_name = 'ads/add_success.html'


class CreateAdWithRegSuccess(TemplateView):
    """Show success page after create new advertisement for guest user
    with information about registration on site."""
    template_name = 'ads/add_success_reg.html'


class LostList(ListView):
    """Lost list advertisements page."""
    template_name = 'ads/lost.html'
    model = Lost
    allow_empty = True
    paginate_by = ADS_PER_PAGE
    filterset_class = TypeFilter

    def get_queryset(self):
        """Creates filterset by filterset_class,
        returns the resulting queryset."""
        queryset = self.model.objects.filter(active=True, open=True)
        self.filterset = self.filterset_class(
            self.request.GET,
            queryset=queryset
        )
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        """Adds additional GET parameters and filter instance to context."""
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        context['parameters'] = (get_copy.pop('page', True)
                                 and get_copy.urlencode())
        context['filter'] = self.filterset
        return context


class FoundList(LostList):
    """Found list advertisements page."""
    template_name = 'ads/found.html'
    model = Found


def map_generation(request, template, model, header, reverse_url):
    ads = model.objects.filter(active=True, open=True)
    f = TypeFilter(request.GET, queryset=ads)
    map_objects = []
    for ad in f.qs:
        if ad.coords:
            if getattr(ad, 'pet_name', ''):
                header_to_show = f'{header}: {ad.pet_name}'
            else:
                header_to_show = header
            hint_content = header_to_show
            if ad.image:
                small_img = get_thumbnail(ad.image, '50x50', crop='center',
                                          quality=99)
                img = f'<img src="/media/{small_img}" class="rounded"'
                balloon_content_header = f'{img} <br> {header_to_show}'
            else:
                balloon_content_header = header_to_show
            if len(ad.description) <= DESCRIPTION_MAP_LIMIT:
                balloon_content_body = ad.description
            else:
                balloon_content_body = (ad.description[:DESCRIPTION_MAP_LIMIT]
                                        + '...')
            url = reverse_lazy(reverse_url, kwargs={'ad_id': ad.id})
            balloon_content_footer = (f'<a href="{url}" '
                                      f'target="_blank">Перейти</a>')
            icon_href = f'/media/{ad.type.icon}'
            map_objects.append({
                "coordinates": list(map(float, ad.coords.split(','))),
                "hintContent": hint_content,
                "balloonContentHeader": balloon_content_header,
                "balloonContentBody": balloon_content_body,
                "balloonContentFooter": balloon_content_footer,
                "iconHref": icon_href
            })
    context = {
        'map_objects': map_objects,
        'filter': f
    }
    return render(request, template, context)


def lost_map(request):
    return map_generation(request, 'ads/lost_map.html', Lost, 'Потерялся',
                          'ads:lost_detail')


def found_map(request):
    return map_generation(request, 'ads/found_map.html', Found, 'Нашелся',
                          'ads:found_detail')


class BaseDetail(DetailView):
    """
    Base class for detail ad pages.
    Only for inheritance.
    """
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'
    pk_url_kwarg = 'ad_id'

    def check_access(self):
        """Only opening and active ads are available on the site.
        The user can see their ads even if they are closed."""
        ad = self.get_object()
        if not (ad.active and ad.open) and ad.author != self.request.user:
            raise Http404

    def get(self, *args, **kwargs):
        self.check_access()
        return super().get(*args, **kwargs)


class LostDetail(BaseDetail):
    """Lost detail ad page."""
    model = Lost

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_title'] = f'Потерялся | {self.object.pet_name}'
        context['ad_model'] = 'l'
        context['age_label'] = 'Возраст'
        context['balloon_content'] = f'Здесь был {self.object.pet_name}'
        context['author_label'] = 'Кто ищет'
        return context


class FoundDetail(BaseDetail):
    """Found detail ad page."""
    model = Found

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_title'] = f'Нашелся | {self.object.type.name}'
        context['ad_model'] = 'f'
        context['age_label'] = 'Примерный возраст'
        context['balloon_content'] = f'Был найден тут'
        context['author_label'] = 'Кто видел'
        return context


class ProfileAdsBase(LoginRequiredMixin, ListView):
    """Base class for user profile ads list pages."""
    template_name = 'ads/my_ads.html'
    paginate_by = ADS_PER_PAGE
    active = True

    def get_active_user_ads(self):
        return (
            self.request.user.lost_ads.filter(active=True, open=True),
            self.request.user.found_ads.filter(active=True, open=True)
        )

    def get_inactive_user_ads(self):
        return (
            self.request.user.lost_ads.filter(Q(active=False) | Q(open=False)),
            self.request.user.found_ads.filter(Q(active=False) | Q(open=False))
        )

    def get_mixed_ads(self):
        to_mix = self.get_active_user_ads()
        to_count = self.get_inactive_user_ads()
        if not self.active:
            to_mix, to_count = to_count, to_mix
        #  https://stackoverflow.com/a/434755/21420819
        ads_mix = sorted(
            chain(*to_mix),
            key=attrgetter('pub_date'),
            reverse=True
        )
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
        context['active_count'] = self.active_count
        context['inactive_count'] = self.inactive_count
        return context


class ProfileActiveList(ProfileAdsBase):
    """View for active ads page of user profile."""
    active = True


class ProfileInactiveList(ProfileAdsBase):
    """Views for inactive ads page of user profile."""
    active = False


@login_required
def profile(request):
    template = 'ads/profile.html'
    form = ChangeNameForm(request.POST or None, instance=request.user)
    if form.is_valid():
        request.user.first_name = form.cleaned_data['first_name']
        request.user.save()
        return redirect(reverse('ads:profile') + '?success=1')
    return render(request, template, {'form': form})


class DialogList(LoginRequiredMixin, ListView):
    """Shows the list of available chats."""
    template_name = 'ads/messages/messages_list.html'
    model = Dialog
    allow_empty = True
    paginate_by = DIALOGS_PER_PAGE
    context_object_name = 'chats'

    def get_queryset(self):
        latest_message_date = Message.objects.filter(
            dialog=OuterRef('pk')).order_by('-pub_date').values('pub_date')[:1]

        chats = Dialog.objects.filter(
            Q(author=self.request.user) | Q(questioner=self.request.user)
        ).annotate(
            latest_message_date=Subquery(latest_message_date)
        ).order_by('-latest_message_date')

        return chats


class MessageChat(LoginRequiredMixin, View):

    def get_dialog(self, request):
        dialog = get_object_or_404(Dialog, pk=self.kwargs['dialog_id'])
        if not (dialog.author == request.user
                or dialog.questioner == request.user):
            raise Http404
        return dialog

    def get(self, request, *args, **kwargs):
        dialog = self.get_dialog(request)

        form = SendMessageForm()
        messages = dialog.messages.order_by('pub_date')
        return render(
            request, 'ads/messages/messages_chat.html', {
                'messages': messages,
                'form': form,
                'advertisement': dialog.advertisement_group
            }
        )

    def post(self, request, *args, **kwargs):
        dialog = self.get_dialog(request)

        form = SendMessageForm(request.POST or None)
        if form.is_valid():
            message = form.save(commit=False)
            message.dialog = dialog
            message.sender = request.user
            message.recipient = dialog.author if dialog.author != request.user else dialog.questioner
            message.save()

        return redirect('ads:messages_chat', self.kwargs['dialog_id'])


class FetchBase(LoginRequiredMixin, View):
    """Class with base functions for fetch requests."""
    MODELS = {
        'l': Lost,
        'f': Found
    }

    def _get_advertisement(self, request):
        request_body = json.loads(request.body.decode())
        ad_type = request_body.get('m')
        ad_id = request_body.get('ad_id')

        try:
            model = self.MODELS[ad_type]
        except KeyError:
            raise BadRequest

        try:
            ad = model.objects.get(pk=ad_id)
        except model.DoesNotExist:
            raise BadRequest

        return ad


class GetContactInfo(FetchBase):
    """Processes fetch-request from ads detail page,
    sends author contact information."""

    def post(self, request):
        try:
            ad = self._get_advertisement(request)
            if not ad.active and ad.author != request.user:
                raise BadRequest
        except BadRequest:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        data = {
            'email': str(ad.author.email),
            'phone': str(ad.author.phone)
        }
        return JsonResponse(data, status=HTTPStatus.OK)


class OpenAd(FetchBase):
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
        return JsonResponse({'message': 'success'}, status=HTTPStatus.OK)


class CloseAd(OpenAd):
    """
    Service view for processing fetch requests from detail post page.
    Allows user to close his advertisement.
    """
    to_set = False


class DialogBase(FetchBase):
    """Base class for dialog views."""
    @staticmethod
    def _get_dialog_ad_field(ad):
        if isinstance(ad, Lost):
            return 'advertisement_lost'
        return 'advertisement_found'


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
                **{self._get_dialog_ad_field(ad): ad}
            )
            dialog_id = dialog.id
        except Dialog.DoesNotExist:
            dialog_id = None

        return JsonResponse({'dialog_id':  dialog_id})


class CreateDialog(DialogBase):
    """Fetch view for create dialog when the first message sent."""

    def post(self, request):
        message = json.loads(request.body.decode()).get('msg').strip()
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
            author=ad.author,
            questioner=request.user,
            **params
        )
        Message.objects.create(
            dialog=dialog,
            sender=request.user,
            recipient=ad.author,
            content=message
        )
        return JsonResponse({'dialog_id': dialog.id})
