# Generated by Django 3.2.3 on 2021-06-15 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('block', '0024_block_text_scale'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='text_scale',
            field=models.FloatField(blank=True, default=14),
        ),
    ]
