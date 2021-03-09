# Generated by Django 2.2.6 on 2020-04-13 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_project_initial_cam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='language_preference',
            field=models.CharField(choices=[('en', 'en'), ('de', 'de')], default='en', max_length=10, verbose_name='lang_pref'),
        ),
    ]
