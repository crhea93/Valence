# Generated by Django 2.2.4 on 2020-02-28 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email address'),
        ),
    ]
