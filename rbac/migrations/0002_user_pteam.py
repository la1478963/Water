# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-08 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pteam',
            field=models.ManyToManyField(blank=True, null=True, related_name='user', to='rbac.Pteam', verbose_name='项目组'),
        ),
    ]
