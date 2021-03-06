# Generated by Django 3.0.2 on 2020-03-29 21:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20200329_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='project',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='users.Project'),
        ),
        migrations.AlterField(
            model_name='cam',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
