# Generated by Django 3.0.2 on 2020-06-10 20:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_auto_20200610_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.DateField(default=datetime.datetime(2020, 6, 10, 20, 26, 58, 859240), verbose_name='Date'),
        ),
    ]
