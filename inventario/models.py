from django.db import models
from django.contrib.auth.models import Group, User 


"""
    Modelo que representa un producto en el inventario.

    Atributos:
    - supply_name: Nombre del producto.
    - supply_code: Código del producto.
    - supply_unit: Unidad de medida del producto.
    - supply_initial_stock: Stock inicial del producto.
    - supply_input: Entrada de stock del producto.
    - supply_output: Salida de stock del producto.
    - supply_total: Stock total actual del producto.

    Métodos:
    - get_nombre_producto(): Retorna el nombre del producto junto con su unidad de medida.

    Meta:
    - verbose_name: Nombre singular del modelo en el panel de administración.
    - verbose_name_plural: Nombre plural del modelo en el panel de administración.
    - ordering: Orden predeterminado para las consultas, ordenado por nombre del producto.
"""
class Product(models.Model):
    supply_name = models.CharField(max_length=100, null=True, blank=True)
    supply_code = models.CharField(max_length=240, null=True, blank=True)
    supply_unit = models.CharField(max_length=240, null=True, blank=True)
    supply_initial_stock = models.CharField(max_length=100, null=True, blank=True, default='No')
    supply_input = models.CharField(max_length=240, null=True, blank=True)
    supply_output = models.CharField(max_length=240, null=True, blank=True)
    supply_total =  models.CharField(max_length=240, null=True, blank=True)

    def get_nombre_producto(self):
        return f'{self.supply_name} ({self.supply_unit})'
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['supply_name']
    
    def __str__(self):
        return self.supply_name

