from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/found/', views.add_found, name='add_found'),
    path('add/lost/', views.add_lost, name='add_lost'),
    path('add/success/', views.add_success, name='add_success'),
    path('lost/list/', views.lost, name='lost'),
    path('found/', views.found, name='found'),
]

