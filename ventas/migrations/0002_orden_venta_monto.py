# Generated by Django 2.0.2 on 2024-05-16 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden_venta',
            name='monto',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
