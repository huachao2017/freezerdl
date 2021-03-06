# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-01-03 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freezers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainrecord',
            name='accuracy_rate',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trainrecord',
            name='duration',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trainrecord',
            name='finish_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='trainrecord',
            name='params',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='trainrecord',
            name='pic_cnt',
            field=models.IntegerField(default=0),
        ),
    ]
