# Generated by Django 2.2.6 on 2019-11-29 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_customuser_block_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cam_pdf',
            field=models.FileField(default='', upload_to=''),
        ),
    ]
