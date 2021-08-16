from django.urls import path
from . import views

app_name = 'YouTubeStats'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/answer', views.search, name='search'),
    path('channel/<int:id>/', views.channel, name='channel'),
    path('add/<str:key>/', views.add, name='add'),
    path('adding/<str:yt_id>/', views.adding_channel, name='adding_channel')
]