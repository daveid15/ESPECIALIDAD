# Generated by Django 2.0.2 on 2024-05-17 22:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0010_auto_20240515_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='proveedor_insumo',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), default=[], size=None),
            preserve_default=False,
        ),
    ]
