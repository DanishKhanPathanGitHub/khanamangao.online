# Generated by Django 5.1 on 2024-09-05 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_userprofile_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='cover_pic',
        ),
    ]
