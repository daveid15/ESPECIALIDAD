# Generated by Django 2.0.2 on 2024-05-03 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0014_auto_20230606_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insumos',
            name='insumos_categorys',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventario.Category'),
        ),
    ]
