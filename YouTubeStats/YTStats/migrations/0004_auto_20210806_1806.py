# Generated by Django 3.2.5 on 2021-08-06 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('YTStats', '0003_auto_20210804_2224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='name',
        ),
        migrations.AddField(
            model_name='channel',
            name='upper_name',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='channel',
            name='yt_name',
            field=models.CharField(default='', max_length=60),
        ),
    ]