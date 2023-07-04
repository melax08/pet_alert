from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/found/', views.add_found, name='add_found'),
    path('add/lost/', views.add_lost, name='add_lost'),
    path('add/success/', views.add_success, name='add_success'),
    path('add/success-reg/', views.add_success_reg, name='add_success_reg'),
    path('lost/list/', views.LostList.as_view(), name='lost'),
    path('lost/map/', views.lost_map, name='lost_map'),
    path('lost/<int:ad_id>/', views.lost_detail, name='lost_detail'),
    path('found/list/', views.FoundList.as_view(), name='found'),
    path('found/<int:ad_id>/', views.found_detail, name='found_detail'),
    path('found/map/', views.found_map, name='found_map'),
    path('profile/', views.profile, name='profile'),
    path('profile/active/', views.ProfileActiveList.as_view(), name='my_ads'),
    path('profile/inactive/',
         views.ProfileInactiveList.as_view(),
         name='my_ads_inactive'
         ),
    path('get/ajax/contact-information/',
         views.get_contact_information,
         name='get_contact_information'
         ),
    path('lost/<int:ad_id>/open/', views.ad_open_lost, name='ad_open_lost'),
    path('lost/<int:ad_id>/close/', views.ad_close_lost, name='ad_close_lost'),
    path('found/<int:ad_id>/open/', views.ad_open_found, name='ad_open_found'),
    path('found/<int:ad_id>/close/',
         views.ad_close_found,
         name='ad_close_found'
         ),
]

