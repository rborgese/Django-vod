# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-13 03:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vod', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(default='cba'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(default='abc', max_length=120),
        ),
    ]