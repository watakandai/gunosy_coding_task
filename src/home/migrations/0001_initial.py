# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-27 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=200)),
            ],
        ),
    ]
