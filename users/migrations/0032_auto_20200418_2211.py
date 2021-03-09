# Generated by Django 3.0.2 on 2020-04-18 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_auto_20200418_2022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='cam_pdf',
            new_name='cam_image',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, default='', null=True, upload_to='../media/avatar/'),
        ),
    ]