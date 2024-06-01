# Generated by Django 2.0.2 on 2024-05-31 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0034_merge_20240531_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='proveedor_insumo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='proveedor_mail',
            field=models.EmailField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='proveedor_rut',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
