# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-10 09:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0025_remove_researchreport_table_raw_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchreport',
            name='table_raw_data',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
