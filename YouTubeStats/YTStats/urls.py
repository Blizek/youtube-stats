from django.urls import path
from . import views

app_name = 'YouTubeStats'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/answer', views.search, name='search'),
    path('channel/<int:id>/overview/', views.channel, name='channel'),
    path('add/<str:key>/', views.add, name='add'),
    path('adding/<str:yt_id>/', views.adding_channel, name='adding_channel'),
    path('channel/<int:id>/subscriptions/', views.subscriptions, name='subscriptions'),
    path('channel/<int:id>/views/', views.views, name='views'),
    path('channel/<int:id>/videos/<str:type_of_sort>/', views.videos, name='videos')
]