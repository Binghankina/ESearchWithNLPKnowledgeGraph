# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-26 08:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0013_auto_20171026_0749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='researchreport',
            name='authors',
        ),
        migrations.AlterField(
            model_name='author',
            name='sec_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
