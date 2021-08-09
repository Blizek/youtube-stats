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
    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    key = request.POST.get('search')
    possible_channels_yt_id = []
    channels_db = Channel.objects.all()
    upper_key = key.upper()

    for channel in channels_db:
        if channel.upper_name in upper_key or channel.url in upper_key or channel.custom_url in upper_key:
            possible_channels_yt_id.append([channel.yt_id, channel.id])

    channels = []
    if len(possible_channels_yt_id) != 0:
        channels_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet, statistics',
            'id': ','.join(c[0] for c in possible_channels_yt_id)
        }

        r = requests.get(channel_url, params=channels_params)
        results = r.json()['items']

        for i in range(len(results)):
            result = results[i]
            channel_data = {
                'id': possible_channels_yt_id[i][1],
                'name': result['snippet']['title'],
                'views': result['statistics']['viewCount'],
                'subscriptions': result['statistics']['subscriberCount'],
                'uploads': result['statistics']['videoCount'],
                'thumbnail': result['snippet']['thumbnails']['default']['url']
            }

            channels.append(channel_data)

        channels.sort(key=subs_sort, reverse=True)

    context = {
        'key': key,
        'channels': channels
    }
    return render(request, 'YTStats/search.html', context)


def channel(request, id):
    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    yt_id_db = Channel.objects.get(pk=id).yt_id
    channel_name = Channel.objects.get(pk=id).name

    channel_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet, statistics',
        'id': yt_id_db
    }

    r = requests.get(channel_url, params=channel_params)

    result = r.json()['items'][0]

    channel_data = {
        'name': result['snippet']['title'],
        'publishedAt': result['snippet']['publishedAt'],
        'thumbnail': result['snippet']['thumbnails']['default']['url'],
        'country': result['snippet']['country'],
        'views': result['statistics']['viewCount'],
        'subscriptions': result['statistics']['subscriberCount'],
        'uploads': result['statistics']['videoCount']
    }

    if 1_000 <= int(channel_data['subscriptions']) < 1_000_000:
        channel_data['subscriptions'] = str(int(channel_data['subscriptions']) / 1_000) + 'K'
    elif 1_000_000 <= int(channel_data['subscriptions']) < 1_000_000_000:
        channel_data['subscriptions'] = str(int(channel_data['subscriptions']) / 1_000_000) + 'M'

    channel_data['publishedAt'] = channel_data['publishedAt'][8:10] + '.' + channel_data['publishedAt'][5:7] + '.' + channel_data['publishedAt'][:4]

    context = {
        'name': channel_name,
        'channel': channel_data
    }

    return render(request, 'YTStats/channel.html', context)


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
                    'uploads': result['statistics']['videoCount'],
                    'thumbnail': result['snippet']['thumbnails']['default']['url']
                }

                channels.append(channel_data)

        channels.sort(key=subs_sort, reverse=True)

    context = {
        'search_key': key,
        'channels': channels
    }
    return render(request, 'YTStats/add.html', context)


def adding_channel(request, yt_id):
    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    channel_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet',
        'id': yt_id,
    }

    r = requests.get(channel_url, params=channel_params)

    result = r.json()['items'][0]

    name = result['snippet']['title']
    upper_name = name.upper()
    custom = result['snippet']['customUrl']
    custom_url = ""
    if len(custom) != 0:
        custom_url = "HTTPS://WWW.YOUTUBE.COM/C/" + custom.upper()

    url = 'HTTPS://WWW.YOUTUBE.COM/CHANNEL/' + yt_id.upper()

    c = Channel(yt_id=yt_id, name=name, upper_name=upper_name, custom_url=custom_url, url=url)
    c.save()

    context = {
        'id': c.id
    }
    return render(request, 'YTStats/adding.html', context)
