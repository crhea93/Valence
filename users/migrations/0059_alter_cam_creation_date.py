# Generated by Django 3.2.5 on 2021-10-20 13:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0058_alter_cam_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cam',
            name='creation_date',
            field=models.CharField(default=datetime.datetime(2021, 10, 20, 13, 20, 24, 898156), max_length=100, verbose_name='Date'),
        ),
    ]