# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-14 03:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vod', '0008_auto_20170414_0326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='content',
        ),
        migrations.RemoveField(
            model_name='post',
            name='height_field',
        ),
        migrations.RemoveField(
            model_name='post',
            name='width_field',
        ),
        migrations.AddField(
            model_name='post',
            name='description',
            field=models.TextField(default='The %s description'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=120),
        ),
    ]