# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-11-30 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToolShare', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrant',
            name='approval_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=225),
        ),
    ]
