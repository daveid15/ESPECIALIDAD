# Generated by Django 2.0.2 on 2024-05-21 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0005_auto_20240520_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden_venta',
            name='id_venta_producto',
        ),
        migrations.AddField(
            model_name='venta_producto',
            name='id_orden',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='ventas.Orden_venta'),
        ),
        migrations.AddField(
            model_name='venta_producto',
            name='precio_producto',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
