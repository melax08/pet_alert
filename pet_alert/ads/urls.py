from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/found/', views.add_found, name='add_found'),
    path('add/lost/', views.add_lost, name='add_lost'),
    path('add/success/', views.add_success, name='add_success'),
    path('lost/list/', views.lost, name='lost'),
    path('lost/map/', views.lost_map, name='lost_map'),
    path('lost/<int:ad_id>/', views.lost_detail, name='lost_detail'),
    path('found/list/', views.found, name='found'),
    path('found/<int:ad_id>/', views.found_detail, name='found_detail'),
    path('found/map/', views.found_map, name='found_map'),
]

