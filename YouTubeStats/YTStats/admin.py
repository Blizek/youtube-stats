from django.contrib import admin

from .models import Channel, Subscriptions, Views, Video

admin.site.register(Channel)
admin.site.register(Subscriptions)
admin.site.register(Views)
admin.site.register(Video)
