# Generated by Django 3.2.5 on 2021-09-06 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('YTStats', '0012_video_update_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='update_date',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_comments',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_dislikes',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_id',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_likes',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_views',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video_youtube_id',
        ),
    ]
