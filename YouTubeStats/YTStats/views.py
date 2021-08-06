import requests

from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.shortcuts import render, redirect

from .models import Channel


def subs_sort(channel):
    return int(channel['subscriptions'])


def index(request):
    template = loader.get_template('YTStats/index.html')
    return HttpResponse(template.render({}, request))


def search(request):
    key = request.POST.get('search')
    template = loader.get_template('YTStats/search.html')
    possible_channels = []
    channels = Channel.objects.all()
    upper_key = key.upper()

    for channel in channels:
        if channel.upper_name in upper_key or channel.url in upper_key or channel.custom_url in upper_key:
            possible_channels.append(channel)

    context = {
        'key': key,
        'channels': possible_channels
    }
    return HttpResponse(template.render(context, request))


def channel(request, id):
    return HttpResponse(id)


def add(request, key):
    channels_db = Channel.objects.all()
    channels_yt_id = [c.yt_id for c in channels_db]
    channels = []

    search_url = 'https://www.googleapis.com/youtube/v3/search'
    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    search_params = {
        'part': 'snippet',
        'q': key,
        'key': settings.YOUTUBE_DATA_API_KEY,
        'type': 'channel',
        'maxResults': 15
    }

    r = requests.get(search_url, params=search_params)

    if r.json()['pageInfo']['totalResults'] != 0:
        results = r.json()['items']

        channels_id = []
        for result in results:
            channels_id.append(result['id']['channelId'])

        channel_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet, statistics',
            'id': ','.join(channels_id),
            'maxResults': 15
        }

        r = requests.get(channel_url, params=channel_params)

        results = r.json()['items']

        for result in results:
            if result['id'] not in channels_yt_id and result['statistics']['hiddenSubscriberCount'] == False:
                channel_data = {
                    'yt_id': result['id'],
                    'name': result['snippet']['title'],
                    'views': result['statistics']['viewCount'],
                    'subscriptions': result['statistics']['subscriberCount'],
                    'uploads': result['statistics']['videoCount']
                }

                channels.append(channel_data)

        channels.sort(key=subs_sort, reverse=True)

    context = {
        'search_key': key,
        'channels': channels
    }
    return render(request, 'YTStats/add.html', context)


def adding_channel(request, yt_id):
    template = loader.get_template('YTStats/adding.html')
    return HttpResponse(template.render({}, request))
