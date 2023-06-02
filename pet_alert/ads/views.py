from itertools import chain

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from sorl.thumbnail import get_thumbnail
from django_registration import signals
from django.conf import settings
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.decorators import login_required

from .models import Found, Lost
from .forms import FoundForm, LostForm, AuthorizedFoundForm, AuthorizedLostForm
from .filters import TypeFilter
from users.forms import CreationForm, CreationFormWithoutPassword


ADS_PER_PAGE = 6
DESCRIPTION_MAP_LIMIT = 60

REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")

EMAIL_BODY_TEMPLATE = 'users/activation_email_body.txt'
EMAIL_SUBJECT_TEMPLATE = 'users/activation_email_subject.txt'


def paginator(request, ads):
    pagination = Paginator(ads, ADS_PER_PAGE)
    page_number = request.GET.get('page')
    return pagination.get_page(page_number)


def index(request):
    template = 'ads/index.html'
    return render(request, template)


class AdWithRegistration(RegistrationView):
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


def add_ad_authorized(request, template, form):
    form = form(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        set_author = form.save(commit=False)
        set_author.author = request.user
        set_author.save()
        return redirect('ads:add_success')
    return render(request, template, {'ad_form': form})


def add_found(request):
    if request.user.is_authenticated:
        return add_ad_authorized(request, 'ads/add_found.html', AuthorizedFoundForm)
    return AdWithRegistration.as_view(template_name='ads/add_found.html')(
        request)


def add_lost(request):
    if request.user.is_authenticated:
        return add_ad_authorized(request, 'ads/add_lost.html', AuthorizedLostForm)
    return AdWithRegistration.as_view(template_name='ads/add_lost.html')(request)


def add_success(request):
    template = 'ads/add_success.html'
    return render(request, template)


def add_success_reg(request):
    template = 'ads/add_success_reg.html'
    return render(request, template)


def ads_list(request, template, model):
    ads = model.objects.filter(active=True)
    f = TypeFilter(request.GET, queryset=ads)
    page_obj = paginator(request, f.qs)
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    context = {
        'page_obj': page_obj,
        'filter': f,
        'parameters': parameters
    }
    return render(request, template, context)


def lost(request):
    return ads_list(request, 'ads/lost.html', Lost)


def found(request):
    return ads_list(request, 'ads/found.html', Found)


def map_generation(request, template, model, header, reverse_url):
    ads = model.objects.filter(active=True)
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


def lost_detail(request, ad_id):
    template = 'ads/lost_detail.html'
    ad = get_object_or_404(Lost, pk=ad_id)
    if not ad.active and ad.author != request.user:
        raise Http404
    context = {
        'ad': ad
    }
    return render(request, template, context)


def found_detail(request, ad_id):
    template = 'ads/found_detail.html'
    ad = get_object_or_404(Found, pk=ad_id)
    if not ad.active and ad.author != request.user:
        raise Http404
    context = {
        'ad': ad
    }
    return render(request, template, context)



@login_required
def my_ads(request):
    template = 'ads/my_ads.html'
    current_user_lost_ads = request.user.lost_ads.filter(active=True)
    current_user_found_ads = request.user.found_ads.filter(active=True)
    mix_ads = list(chain(current_user_lost_ads, current_user_found_ads))
    page_obj = paginator(request, mix_ads)

    inactive_count = (request.user.lost_ads.filter(active=False).count()
                      + request.user.found_ads.filter(active=False).count())
    context = {
        'page_obj': page_obj,
        'active_count': len(mix_ads),
        'inactive_count': inactive_count
    }
    return render(request, template, context)


@login_required
def my_ads_inactive(request):
    template = 'ads/my_ads.html'
    current_user_lost_ads = request.user.lost_ads.filter(active=False)
    current_user_found_ads = request.user.found_ads.filter(active=False)
    mix_ads = list(chain(current_user_lost_ads, current_user_found_ads))
    page_obj = paginator(request, mix_ads)

    active_count = (request.user.lost_ads.filter(active=True).count()
                    + request.user.found_ads.filter(active=True).count())

    context = {
        'page_obj': page_obj,
        'active_count': active_count,
        'inactive_count': len(mix_ads)
    }
    return render(request, template, context)
