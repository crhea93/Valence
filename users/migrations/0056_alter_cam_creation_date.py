# Generated by Django 3.2 on 2021-10-19 01:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0055_alter_cam_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.CharField(default=datetime.datetime(2021, 10, 19, 1, 17, 20, 248356), max_length=100, verbose_name='Date'),
        ),
    ]
