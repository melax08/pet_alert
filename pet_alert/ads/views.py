from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from sorl.thumbnail import get_thumbnail
from django_registration import signals
from django.core import signing
from django_registration.backends.activation.views import ActivationView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password
from django.views.generic import DetailView
from django.contrib.auth.forms import SetPasswordForm
from django.views.generic.edit import FormView
from django_registration.exceptions import ActivationError
from django.contrib.auth import login as auth_login
from django.utils.encoding import force_str

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


INTERNAL_SET_PASS_SESSION_TOKEN = "_password_set_token"


def set_password(request):
    def validate_key(activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or raising ``ActivationError`` if not.

        """
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400,
            )
            return username
        except signing.SignatureExpired:
            raise ActivationError('Просрочено', code="expired")
        except signing.BadSignature:
            raise ActivationError(
                'Неправильный ключ',
                code="invalid_key",
                params={"activation_key": activation_key},
            )

    def get_user(username):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or raising
        ``ActivationError`` if it doesn't.

        """
        User = get_user_model()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
            if user.is_active:
                raise ActivationError(
                    'Уже активен', code="already_activated"
                )
            return user
        except User.DoesNotExist:
            raise ActivationError('Такого юзера не существует', code="bad_username")

    session_token = request.session.get(INTERNAL_SET_PASS_SESSION_TOKEN)
    try:
        username = validate_key(session_token)
        user = get_user(username)
    except (ActivationError, TypeError):
        return render(request, 'users/password_reset_confirm.html', {'validlink': False})
    form = SetPasswordForm(user, request.POST or None)
    if form.is_valid():
        user.is_active = True
        user.save()
        # Переписать форму SetPasswordForm, чтобы в методе save() делала юзера активным
        form.save()
        auth_login(request, user)
        if INTERNAL_SET_PASS_SESSION_TOKEN in request.session:
            del request.session[INTERNAL_SET_PASS_SESSION_TOKEN]
        signals.user_activated.send(
            sender=set_password.__class__, user=user, request=request
        )
        return redirect(reverse_lazy('users:set_password_done'))
    return render(request, 'users/password_reset_confirm.html', {'form': form, 'validlink': True})


class CustomActivationView(ActivationView):
    set_url_link = 'set-password'
    form_class = SetPasswordForm

    def activate(self, *args, **kwargs):
        key = kwargs.get('activation_key')
        username = self.validate_key(kwargs.get("activation_key"))
        user = self.get_user(username)
        if check_password('', user.password):
            self.request.session[INTERNAL_SET_PASS_SESSION_TOKEN] = key
            # redirect_url = self.request.path.replace(
            #     key, self.set_url_link
            # )
            # return HttpResponseRedirect(redirect_url)
        else:
            user.is_active = True
            user.save()
        return user

    def get(self, *args, **kwargs):
        extra_context = {}
        try:
            activated_user = self.activate(*args, **kwargs)
        except ActivationError as e:
            extra_context["activation_error"] = {
                "message": e.message,
                "code": e.code,
                "params": e.params,
            }
        else:
            if check_password('', activated_user.password):
                self.request.session[INTERNAL_SET_PASS_SESSION_TOKEN] = kwargs.get('activation_key')
                return redirect('ads:set_password')
            else:
                signals.user_activated.send(
                    sender=self.__class__, user=activated_user, request=self.request
                )
                return HttpResponseRedirect(force_str(self.get_success_url(activated_user)))
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)


def add_ad_authorized(request, template, form):
    form = form(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        set_address = form.save(commit=False)
        set_address.address = request.POST['address']
        set_address.coords = request.POST['coords']
        set_address.author = request.user
        set_address.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})


def add_ad_unauthorized(request, template, form):

    def send_activation_email(user):
        activation_key = get_activation_key(user)
        context = get_email_context(activation_key)
        context["user"] = user
        subject = render_to_string(
            template_name=EMAIL_SUBJECT_TEMPLATE,
            context=context,
            request=request,
        )
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = "".join(subject.splitlines())
        message = render_to_string(
            template_name=EMAIL_BODY_TEMPLATE,
            context=context,
            request=request,
        )
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def get_activation_key(user):
        return signing.dumps(obj=user.get_username(), salt=REGISTRATION_SALT)

    def get_email_context(activation_key):
        scheme = "https" if request.is_secure() else "http"
        return {
            "scheme": scheme,
            "activation_key": activation_key,
            "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
            "site": get_current_site(request),
        }

    form = form(request.POST or None, files=request.FILES or None)
    reg_form = CreationFormWithoutPassword(request.POST or None)
    if form.is_valid() and reg_form.is_valid():
        reg_user = reg_form.save(commit=False)
        reg_user.is_active = False
        reg_user.save()
        signals.user_registered.send(
            sender=add_ad_unauthorized.__class__, user=reg_user, request=request
        )
        send_activation_email(reg_user)
        set_address = form.save(commit=False)
        set_address.address = request.POST['address']
        set_address.coords = request.POST['coords']
        set_address.author = reg_user
        set_address.save()
        return redirect('ads:add_success_reg')
    return render(request, template, {'form': form, 'reg_form': reg_form})


def add_found(request):
    if request.user.is_authenticated:
        return add_ad_authorized(request, 'ads/add_found.html', AuthorizedFoundForm)
    return add_ad_unauthorized(request, 'ads/add_found.html', FoundForm)


def add_lost(request):
    if request.user.is_authenticated:
        return add_ad_authorized(request, 'ads/add_lost.html', AuthorizedLostForm)
    return add_ad_unauthorized(request, 'ads/add_lost.html', LostForm)


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
    ad = get_object_or_404(Lost, pk=ad_id, active=True)
    context = {
        'ad': ad
    }
    return render(request, template, context)


def found_detail(request, ad_id):
    template = 'ads/found_detail.html'
    ad = get_object_or_404(Found, pk=ad_id, active=True)
    context = {
        'ad': ad
    }
    return render(request, template, context)

