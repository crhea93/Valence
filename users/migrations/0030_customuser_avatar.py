# Generated by Django 3.0.2 on 2020-04-18 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_auto_20200418_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
