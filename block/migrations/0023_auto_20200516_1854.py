# Generated by Django 3.0.2 on 2020-05-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('block', '0022_block_cam'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='height',
            field=models.FloatField(default=120),
        ),
        migrations.AddField(
            model_name='block',
            name='width',
            field=models.FloatField(default=160),
        ),
    ]