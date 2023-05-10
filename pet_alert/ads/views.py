from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from sorl.thumbnail import get_thumbnail

from .models import Found, Lost
from .forms import FoundForm, LostForm
from .filters import TypeFilter

ADS_PER_PAGE = 6
DESCRIPTION_MAP_LIMIT = 60


def paginator(request, ads):
    pagination = Paginator(ads, ADS_PER_PAGE)
    page_number = request.GET.get('page')
    return pagination.get_page(page_number)


def index(request):
    template = 'ads/index.html'
    return render(request, template)


def add_ad(request, template, form):
    form = form(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        set_address = form.save(commit=False)
        set_address.address = request.POST['address']
        set_address.coords = request.POST['coords']
        set_address.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})


def add_found(request):
    return add_ad(request, 'ads/add_found.html', FoundForm)


def add_lost(request):
    return add_ad(request, 'ads/add_lost.html', LostForm)


def add_success(request):
    template = 'ads/add_success.html'
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

