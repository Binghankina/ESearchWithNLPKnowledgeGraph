# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-26 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0014_auto_20171026_0855'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchreport',
            name='authors',
            field=models.ManyToManyField(to='rest_api.Author'),
        ),
    ]
