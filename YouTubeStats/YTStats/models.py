from django.db import models


class Channel(models.Model):
    yt_id = models.CharField(max_length=24, default='')
    name = models.CharField(max_length=60, default='')
    upper_name = models.CharField(max_length=60, default='')
    custom_url = models.CharField(max_length=60, default='')
    url = models.CharField(max_length=56, default='')

    def __str__(self):
        return self.name


class Subscriptions(models.Model):
    subs_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    subs_value = models.IntegerField(default=0)
    update_date = models.DateTimeField('update date')

    def __str__(self):
        return str(self.subs_value)
