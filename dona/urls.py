from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check', views.check, name='check'),
    path('get_item', views.get_item, name='get_item'),
    path('get_mono', views.get_mono, name='get_mono'),
    path('get_gei', views.get_gei, name='get_gei'),
    path('output_item', views.output_item, name='output_item'),
    path('output_mono', views.output_mono, name='output_mono'),
    path('output_gei', views.output_gei, name='output_gei'),
    path('output_item_mono', views.output_item_mono, name='output_item_mono'),
    path('output_item_mono_gei', views.output_item_mono_gei,
         name='output_item_mono_gei'),
]
