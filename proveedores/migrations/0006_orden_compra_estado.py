# Generated by Django 2.0.2 on 2024-05-13 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0005_auto_20240508_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden_compra',
            name='estado',
            field=models.CharField(choices=[('enviado', 'Enviado'), ('rechazado', 'Rechazado'), ('aceptado', 'Aceptado'), ('anulado', 'Anulado')], default='enviado', max_length=20),
        ),
    ]
