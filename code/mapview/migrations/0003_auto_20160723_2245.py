# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-23 22:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapview', '0002_player_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=550, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('state', models.BooleanField(default=False, help_text='if true than this user will be active')),
            ],
        ),
        migrations.CreateModel(
            name='CityPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lon', models.FloatField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='mapview.City')),
            ],
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ('created_date',)},
        ),
    ]
