from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from sorl.thumbnail import get_thumbnail

from .models import Found, Lost
from .forms import FoundForm, LostForm

ADS_COUNT = 10


def paginator(request, ads):
    pagination = Paginator(ads, ADS_COUNT)
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


def lost(request):
    template = 'ads/lost.html'
    ads = Lost.objects.filter(active=True)
    page_obj = paginator(request, ads)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def found(request):
    template = 'ads/found.html'
    ads = Found.objects.filter(active=True)
    page_obj = paginator(request, ads)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def lost_map(request):
    template = 'ads/lost_map.html'
    ads = Lost.objects.filter(active=True)
    map_objects = []
    for ad in ads:
        hint_content = ad.pet_name
        small_img = get_thumbnail(ad.image, '50x50', crop='center', quality=99)
        img = f'<img src="/media/{small_img}" class="rounded"'
        balloon_content_header = f'{img} <br> Потерялся: {ad.pet_name}'
        balloon_content_body = ad.description
        url = reverse_lazy('ads:lost_detail', kwargs={'ad_id': ad.id})
        balloon_content_footer = f'<a href="{url}">Перейти</a>'
        map_objects.append({
            "coordinates": list(map(float, ad.coords.split(','))),
            "hintContent": hint_content,
            "balloonContentHeader": balloon_content_header,
            "balloonContentBody": balloon_content_body,
            "balloonContentFooter": balloon_content_footer
        })
    context = {
        'map_objects': map_objects
    }
    return render(request, template, context)


def found_map(request):
    template = 'ads/found_map.html'
    ads = Found.objects.filter(active=True)
    map_objects = []
    for ad in ads:
        hint_content = 'Нашелся'
        small_img = get_thumbnail(ad.image, '50x50', crop='center', quality=99)
        img = f'<img src="/media/{small_img}" class="rounded"'
        balloon_content_header = f'{img} <br> Нашелся:'
        balloon_content_body = ad.description
        url = reverse_lazy('ads:found_detail', kwargs={'ad_id': ad.id})
        balloon_content_footer = f'<a href="{url}">Перейти</a>'
        map_objects.append({
            "coordinates": list(map(float, ad.coords.split(','))),
            "hintContent": hint_content,
            "balloonContentHeader": balloon_content_header,
            "balloonContentBody": balloon_content_body,
            "balloonContentFooter": balloon_content_footer
        })
    context = {
        'map_objects': map_objects
    }
    return render(request, template, context)


def lost_detail(request, ad_id):
    template = 'ads/lost_detail.html'
    ad = get_object_or_404(Lost,
                           pk=ad_id,
                           active=True
                           )
    context = {
        'ad': ad
    }
    return render(request, template, context)


def found_detail(request, ad_id):
    template = 'ads/found_detail.html'
    ad = get_object_or_404(Found,
                           pk=ad_id,
                           active=True
                           )
    context = {
        'ad': ad
    }
    return render(request, template, context)

