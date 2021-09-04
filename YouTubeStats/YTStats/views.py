import requests
from datetime import datetime

from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader
from django.conf import settings
from django.shortcuts import render

from .models import Channel, Subscriptions


def subs_sort(channel):
    return int(channel['subscriptions'])


def add_commas(views):
    views = views[::-1]
    iterations = []
    for i in range(3, len(views) + 3, 3):
        iterations.append(views[i - 3: i][::-1])
    views = ','.join(iterations[::-1])
    return views


def covert_date(date):
    return date[8:10] + '.' + date[5:7] + '.' + date[:4]


def convert_timezone(timezone_date):
    data = str(covert_date(str(timezone_date)) + ' ' + str(timezone_date)[11:19])
    return data


def add_prefix(number):
    if 1_000 <= number < 1_000_000:
        shorter = number / 1_000
        if shorter % 1 == 0:
            shorter = int(shorter)
        return str(shorter) + 'K'
    elif 1_000_000 <= number < 1_000_000_000:
        shorter = number / 1_000_000
        if shorter % 1 == 0:
            shorter = int(shorter)
        return str(shorter) + 'M'
    return number


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

        for channel in channels:
            channel['subscriptions'] = add_prefix(int(channel['subscriptions']))
            channel['views'] = add_commas(str(channel['views']))
            channel['uploads'] = add_commas(str(channel['uploads']))

    context = {
        'key': key,
        'channels': channels
    }
    return render(request, 'YTStats/search.html', context)


def channel(request, id):
    channel_url = 'https://www.googleapis.com/youtube/v3/channels'
    search_url = 'https://www.googleapis.com/youtube/v3/search'

    yt_id_db = Channel.objects.get(pk=id).yt_id
    channel_name = Channel.objects.get(pk=id).name

    channel_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet, statistics, brandingSettings',
        'id': yt_id_db
    }

    r = requests.get(channel_url, params=channel_params)

    result = r.json()['items'][0]

    channel_data = {
        'name': result['snippet']['title'],
        'publishedAt': covert_date(result['snippet']['publishedAt']),
        'thumbnail': result['snippet']['thumbnails']['default']['url'],
        'views': add_commas(str(result['statistics']['viewCount'])),
        'subscriptions': add_prefix(int(result['statistics']['subscriberCount'])),
        'uploads': add_commas(str(result['statistics']['videoCount'])),
        'lastVideoID': ""
    }

    try:
        channel_data['country'] = str(result['snippet']['country'])
    except KeyError:
        channel_data['country'] = ""

    try:
        channel_data['banner'] = result['brandingSettings']['image']['bannerExternalUrl']
    except KeyError:
        channel_data['banner'] = ""

    search_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet',
        'channelId': yt_id_db,
        'maxResults': 1,
        'type': 'video',
        'order': 'date',
        'q': channel_name,
    }

    r_search = requests.get(search_url, params=search_params)

    result_search = r_search.json()

    if result_search['pageInfo']['totalResults'] != 0:
        channel_data['lastVideoID'] = result_search['items'][0]['id']['videoId']

    context = {
        'name': channel_name,
        'channel': channel_data,
        'id': id
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

        for channel in channels:
            channel['subscriptions'] = add_prefix(int(channel['subscriptions']))
            channel['views'] = add_commas(str(channel['views']))
            channel['uploads'] = add_commas(str(channel['uploads']))

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
    try:
        custom = result['snippet']['customUrl']
    except KeyError:
        custom = ""
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


def subscriptions(request, id):
    channel_yt_id = Channel.objects.get(pk=id).yt_id
    channel_name = Channel.objects.get(pk=id).name

    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    channel_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'statistics',
        'id': channel_yt_id
    }

    r = requests.get(channel_url, params=channel_params)

    result = r.json()['items'][0]

    c = Channel.objects.get(pk=id)
    c.subscriptions_set.create(subs_value=result['statistics']['subscriberCount'], update_date=timezone.now())

    converted_data = []

    for subscription_data in c.subscriptions_set.all():
        data = {
            'subs_value': add_prefix(subscription_data.subs_value),
            'update_date': convert_timezone(subscription_data.update_date)
        }

        converted_data.append(data)

    context = {
        'name': channel_name,
        'subscriptions_data': converted_data
    }

    return render(request, 'YTStats/subscriptions.html', context)


def views(request, id):
    channel_yt_id = Channel.objects.get(pk=id).yt_id
    channel_name = Channel.objects.get(pk=id).name

    channel_url = 'https://www.googleapis.com/youtube/v3/channels'

    channel_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'statistics',
        'id': channel_yt_id
    }

    r = requests.get(channel_url, params=channel_params)

    result = r.json()['items'][0]

    c = Channel.objects.get(pk=id)
    c.views_set.create(views_value=result['statistics']['viewCount'], update_date=timezone.now())

    converted_data = []

    for views_data in c.views_set.all():
        data = {
            'views_value': add_commas(str(views_data.views_value)),
            'update_date': convert_timezone(views_data.update_date)
        }

        converted_data.append(data)

    context = {
        'name': channel_name,
        'views_data': converted_data
    }

    return render(request, 'YTStats/views.html', context)


def videos(request, id, type_of_sort):
    channel_yt_id = Channel.objects.get(pk=id).yt_id
    channel_name = Channel.objects.get(pk=id).name

    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    search_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet',
        'channelId': channel_yt_id,
        'maxResults': 50,
        'type': 'video',
        'order': type_of_sort,
        'q': channel_name,
    }

    r = requests.get(search_url, params=search_params)

    results = r.json()['items']

    videos_id_list = []

    for result in results:
        videos_id_list.append(result['id']['videoId'])

    video_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet, statistics',
        'id': ','.join(videos_id_list),
        'maxResults': 50
    }

    r = requests.get(video_url, params=video_params)

    results = r.json()['items']

    videos_data_list = []

    for result in results:
        video_data = {
            'title': result['snippet']['title'],
            'publishedAt': covert_date(result['snippet']['publishedAt']),
            'thumbnail': result['snippet']['thumbnails']['default']['url'],
            'views': add_commas(result['statistics']['viewCount']),
            'comments': add_commas(result['statistics']['commentCount']),
            'likesRatio': round(100 * int(result['statistics']['likeCount']) / (
                    int(result['statistics']['dislikeCount']) + int(result['statistics']['likeCount'])), 1),
            'videoUrl': 'https://www.youtube.com/watch?v=' + result['id']
        }

        videos_data_list.append(video_data)

    context = {
        'videos': videos_data_list,
        'name': channel_name,
        'id': id
    }

    return render(request, 'YTStats/videos.html', context)
