# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-06 16:31
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0022_remove_researchreport_attachment_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchreport',
            name='attachment_images',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=[], null=True, size=None),
        ),
    ]
