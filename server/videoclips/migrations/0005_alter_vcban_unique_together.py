# Generated by Django 4.0.6 on 2022-08-21 19:38

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoclips', '0004_rename_baned_user_vcban_banned_user'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vcban',
            unique_together={('videoclip', 'banned_user')},
        ),
    ]
