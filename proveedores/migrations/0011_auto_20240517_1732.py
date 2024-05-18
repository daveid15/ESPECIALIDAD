# Generated by Django 2.0.2 on 2024-05-17 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0010_auto_20240515_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orden_compra',
            name='cantidad_orden',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='orden_compra',
            name='producto_orden',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proveedores.Producto'),
        ),
        migrations.AlterField(
            model_name='orden_compra',
            name='proveedor_orden',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proveedores.Proveedor'),
        ),
    ]
