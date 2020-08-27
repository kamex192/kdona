from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check', views.check, name='check'),
    path('get_info', views.get_info, name='get_info'),
    path('get_mono', views.get_mono, name='get_mono'),
    path('get_gei', views.get_gei, name='get_gei'),
]
