# Generated by Django 5.1 on 2024-12-03 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0008_alter_openinghours_from_hour_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinghours',
            name='from_hour',
            field=models.CharField(blank=True, choices=[('12:00 AM', '12:00 AM'), ('01:30 AM', '01:30 AM'), ('02:30 AM', '02:30 AM'), ('03:30 AM', '03:30 AM'), ('04:30 AM', '04:30 AM'), ('05:30 AM', '05:30 AM'), ('06:30 AM', '06:30 AM'), ('07:30 AM', '07:30 AM'), ('08:30 AM', '08:30 AM'), ('09:30 AM', '09:30 AM'), ('10:30 AM', '10:30 AM'), ('11:30 AM', '11:30 AM'), ('12:30 PM', '12:30 PM'), ('01:30 PM', '01:30 PM'), ('02:30 PM', '02:30 PM'), ('03:30 PM', '03:30 PM'), ('04:30 PM', '04:30 PM'), ('05:30 PM', '05:30 PM'), ('06:30 PM', '06:30 PM'), ('07:30 PM', '07:30 PM'), ('08:30 PM', '08:30 PM'), ('09:30 PM', '09:30 PM'), ('10:30 PM', '10:30 PM'), ('11:30 PM', '11:30 PM'), ('11:59 PM', '11:59 PM')]),
        ),
        migrations.AlterField(
            model_name='openinghours',
            name='to_hour',
            field=models.CharField(blank=True, choices=[('12:00 AM', '12:00 AM'), ('01:30 AM', '01:30 AM'), ('02:30 AM', '02:30 AM'), ('03:30 AM', '03:30 AM'), ('04:30 AM', '04:30 AM'), ('05:30 AM', '05:30 AM'), ('06:30 AM', '06:30 AM'), ('07:30 AM', '07:30 AM'), ('08:30 AM', '08:30 AM'), ('09:30 AM', '09:30 AM'), ('10:30 AM', '10:30 AM'), ('11:30 AM', '11:30 AM'), ('12:30 PM', '12:30 PM'), ('01:30 PM', '01:30 PM'), ('02:30 PM', '02:30 PM'), ('03:30 PM', '03:30 PM'), ('04:30 PM', '04:30 PM'), ('05:30 PM', '05:30 PM'), ('06:30 PM', '06:30 PM'), ('07:30 PM', '07:30 PM'), ('08:30 PM', '08:30 PM'), ('09:30 PM', '09:30 PM'), ('10:30 PM', '10:30 PM'), ('11:30 PM', '11:30 PM'), ('11:59 PM', '11:59 PM')]),
        ),
    ]
