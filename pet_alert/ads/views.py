from django.shortcuts import render


def index(request):
    template = 'ads/index.html'
    return render(request, template)

