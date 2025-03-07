# Generated by Django 2.0.2 on 2024-05-27 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0022_auto_20240525_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='supply_initial_stock',
            field=models.CharField(blank=True, default='No', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='supply_input',
            field=models.CharField(blank=True, max_length=240, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='supply_output',
            field=models.CharField(blank=True, max_length=240, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='supply_total',
            field=models.CharField(blank=True, max_length=240, null=True),
        ),
    ]
