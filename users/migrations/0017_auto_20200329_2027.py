# Generated by Django 3.0.2 on 2020-03-29 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20200328_2215'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='user',
            new_name='researcher',
        ),
    ]
