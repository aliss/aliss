# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-04-11 11:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aliss', '0013_auto_20180411_0958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claim',
            name='created_by',
        ),
    ]
