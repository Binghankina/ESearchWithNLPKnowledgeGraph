# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-26 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0015_researchreport_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='expire_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='grant_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
