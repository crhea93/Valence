# Generated by Django 2.2.6 on 2020-06-08 23:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_cam_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.DateField(default=datetime.datetime.now, verbose_name='Date'),
        ),
    ]
