# Generated by Django 2.2.4 on 2020-02-29 23:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('block', '0019_auto_20200229_2318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='block',
            old_name='undeletable',
            new_name='modifiable',
        ),
    ]
