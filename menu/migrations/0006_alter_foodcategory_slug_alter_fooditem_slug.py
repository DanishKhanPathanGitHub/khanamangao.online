# Generated by Django 5.0.4 on 2024-08-26 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_alter_foodcategory_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodcategory',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]
