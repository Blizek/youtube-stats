# Generated by Django 3.2.5 on 2021-09-06 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('YTStats', '0010_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_id',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='YTStats.channel'),
        ),
    ]