# Generated by Django 3.2.5 on 2021-10-27 20:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0060_merge_20211027_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.CharField(default=datetime.datetime(2021, 10, 27, 20, 4, 0, 668756), max_length=100, verbose_name='Date'),
        ),
    ]
