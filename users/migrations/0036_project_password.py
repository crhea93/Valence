# Generated by Django 2.2.6 on 2020-05-30 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_auto_20200418_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='password',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
