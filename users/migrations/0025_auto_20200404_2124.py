# Generated by Django 3.0.2 on 2020-04-04 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20200403_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name_participants',
            field=models.CharField(default='', max_length=10, unique=True),
        ),
    ]
