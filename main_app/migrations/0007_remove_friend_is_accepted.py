# Generated by Django 5.1.2 on 2024-11-18 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_friend_is_accepted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friend',
            name='is_accepted',
        ),
    ]
