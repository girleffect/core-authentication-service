# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-02 13:43
from __future__ import unicode_literals

import authentication_service.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication_service', '0007_auto_20180502_0905'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='coreuser',
            index=authentication_service.models.TrigramIndex(fields=['msisdn'], name='authenticat_msisdn_848b4b_gin'),
        ),
    ]
