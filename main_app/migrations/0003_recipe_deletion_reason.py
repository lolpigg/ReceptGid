# Generated by Django 5.1.2 on 2024-11-05 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='deletion_reason',
            field=models.TextField(default=None, null=True),
        ),
    ]