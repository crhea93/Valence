# Generated by Django 2.2.2 on 2019-06-29 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='border_color',
            new_name='line_color',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='border_style',
            new_name='line_style',
        ),
    ]
