# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-06-10 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aliss', '0035_remove_alissuser_email_two'),
    ]

    operations = [
        migrations.AddField(
            model_name='alissuser',
            name='is_account_owner',
            field=models.BooleanField(default=False),
        ),
    ]
