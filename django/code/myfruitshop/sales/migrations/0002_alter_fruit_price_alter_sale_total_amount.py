# Generated by Django 4.2 on 2023-12-11 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fruit',
            name='price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='sale',
            name='total_amount',
            field=models.PositiveIntegerField(),
        ),
    ]
