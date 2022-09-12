from django.shortcuts import render
from django.shortcuts import redirect

from .models import Found, Lost
from .forms import FoundForm, LostForm


def index(request):
    template = 'ads/index.html'
    return render(request, template)


def add_found(request):
    template = 'ads/add_found.html'
    form = FoundForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})


def add_lost(request):
    template = 'ads/add_lost.html'
    form = LostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('ads:add_success')
    return render(request, template, {'form': form})
