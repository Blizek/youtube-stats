from django.db import models


class Channel(models.Model):
    yt_id = models.CharField(max_length=24, default='')
    name = models.CharField(max_length=60, default='')
    upper_name = models.CharField(max_length=60, default='')
    custom_url = models.CharField(max_length=60, default='')
    url = models.CharField(max_length=56, default='')

    def __str__(self):
        return self.name
