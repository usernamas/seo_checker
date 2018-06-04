from django.urls import path

from . import views

app_name = 'checkup'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('seo/', views.SeoView.as_view(), name='seo'),
    path('broken_links/', views.IndexView.broken_links, name='broken_links'),
    path('keywords/', views.IndexView.keywords, name='keywords'),
    path('render_template/', views.IndexView.render_template, name='render_template')
]