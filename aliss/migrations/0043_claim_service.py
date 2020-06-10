# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-06-10 09:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aliss', '0042_remove_claim_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='service',
            field=models.ForeignKey(default='SOME STRING', on_delete=django.db.models.deletion.CASCADE, to='aliss.Service'),
            preserve_default=False,
        ),
    ]
