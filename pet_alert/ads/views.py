from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator

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


def add_found(request):
    template = 'ads/add_found.html'
    form = FoundForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        set_address = form.save(commit=False)
        set_address.address = request.POST['address']
        set_address.coords = request.POST['coords']
        set_address.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})


def add_lost(request):
    template = 'ads/add_lost.html'
    form = LostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        set_address = form.save(commit=False)
        set_address.address = request.POST['address']
        set_address.coords = request.POST['coords']
        set_address.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})


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


def lost_map(request):
    template = 'ads/lost_map.html'
    ads = Lost.objects.filter(active=True)
    coords = []
    for ad in ads:
        coords.append(list(map(float, ad.coords.split(','))))
    context = {
        'coords': coords
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


def found(request):
    pass
