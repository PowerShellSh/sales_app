# Generated by Django 4.2 on 2023-12-13 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_fruit_is_active_alter_sale_fruit'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
