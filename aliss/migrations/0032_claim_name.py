# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-07-08 07:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aliss', '0031_auto_20200701_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
