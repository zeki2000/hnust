# Generated by Django 4.0.8 on 2025-04-04 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='avatar',
            field=models.URLField(default='assets/img/avatars/default_1.png', max_length=255, verbose_name='头像URL'),
        ),
    ]
