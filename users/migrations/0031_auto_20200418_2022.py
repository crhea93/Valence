# Generated by Django 3.0.2 on 2020-04-18 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_customuser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='', null=True, upload_to='avatars/'),
        ),
    ]
