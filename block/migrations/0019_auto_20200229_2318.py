# Generated by Django 2.2.4 on 2020-02-29 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('block', '0018_auto_20200226_1644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='block',
            old_name='modifiable',
            new_name='undeletable',
        ),
    ]
