# Generated by Django 2.0.2 on 2024-05-17 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0013_auto_20240517_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orden_compra',
            name='proveedor_orden',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proveedores.Proveedor'),
        ),
    ]
