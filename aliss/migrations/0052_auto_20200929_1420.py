# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-09-29 14:20
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aliss', '0051_claim_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='phone',
            field=models.CharField(default='', max_length=30, validators=[django.core.validators.RegexValidator(code='nomatch', message='Length has to be 11', regex='^.{11}$')]),
        ),
    ]
