import requests

from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import render, redirect

from .models import Channel


def index(request):
    # channel_url = 'https://www.googleapis.com/youtube/v3/channels'
    #
    # params = {
    #     'part': 'snippet, statistics, topicDetails',
    #     # 'id': "UCwBtP6NDQtsP5YBa4vuZqHA",
    #     'id': 'UClLY25Wt_fuaEjFjskmW8kg',
    #     'key': settings.YOUTUBE_DATA_API_KEY
    # }
    #
    # r = requests.get(channel_url, params=params)
    # print(r.text)
    template = loader.get_template('YTStats/index.html')
    return HttpResponse(template.render({}, request))


def search(request):
    key = request.POST.get('search')
    template = loader.get_template('YTStats/search.html')
    possible_channels = []
    channels = Channel.objects.all()
    upper_key = key.upper()

    for channel in channels:
        print(channel, upper_key)
        if upper_key in channel.name or upper_key in channel.url or upper_key in channel.custom_url:
            possible_channels.append(channel)

    context = {
        'key': key,
        'channels': possible_channels
    }
    return HttpResponse(template.render(context, request))


def channel(request, id):
    return HttpResponse(id)
