# Generated by Django 5.0.4 on 2024-08-23 02:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_rename_lattitued_userprofile_latitued'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='latitued',
            new_name='latitude',
        ),
    ]