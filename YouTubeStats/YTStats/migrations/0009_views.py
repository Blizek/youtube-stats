# Generated by Django 3.2.5 on 2021-09-04 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('YTStats', '0008_subscriptions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Views',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('views_value', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(verbose_name='update date')),
                ('views_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='YTStats.channel')),
            ],
        ),
    ]
