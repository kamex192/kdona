from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check', views.check, name='check'),
    path('get_rakuten_books', views.get_rakuten_books, name='get_rakuten_books'),
    path('get_mono', views.get_mono, name='get_mono'),
    path('get_antlion', views.get_antlion, name='get_antlion'),
    path('get_gei', views.get_gei, name='get_gei'),
    path('get_penguin', views.get_penguin, name='get_penguin'),
    path('dell_all_gei', views.dell_all_gei, name='dell_all_gei'),
    path('output_rakuten_books', views.output_rakuten_books,
         name='output_rakuten_books'),
    path('output_mono', views.output_mono, name='output_mono'),
    path('output_antlion', views.output_antlion, name='output_antlion'),
    path('output_gei', views.output_gei, name='output_gei'),
    path('output_penguin', views.output_penguin, name='output_penguin'),
    path('output_gei_antlion', views.output_gei_antlion, name='output_gei_antlion'),
    path('output_item_mono', views.output_item_mono, name='output_item_mono'),
    path('output_item_mono_gei', views.output_item_mono_gei,
         name='output_item_mono_gei'),
]
