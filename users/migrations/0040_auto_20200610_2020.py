# Generated by Django 3.0.2 on 2020-06-10 20:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_auto_20200610_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.DateField(default=datetime.datetime(2020, 6, 10, 20, 20, 2, 278905, tzinfo=utc), verbose_name='Date'),
        ),
    ]
