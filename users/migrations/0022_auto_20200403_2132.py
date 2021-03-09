# Generated by Django 3.0.2 on 2020-04-03 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20200329_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='part_name',
            field=models.CharField(default='', max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(default='', max_length=50, unique=True),
        ),
    ]
