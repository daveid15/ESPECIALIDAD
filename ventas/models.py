from django.db import models
from django.contrib.auth.models import Group, User 

class Prod_venta(models.Model):
    nombre_producto = models.CharField(max_length=100, null=True, blank=True, default='')
    precio = models.PositiveIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f'{self.nombre_producto}'  # Asegurándote de devolver el nombre del producto
    
class Orden_venta(models.Model):
    numero_orden = models.AutoField(primary_key=True)
    cliente_venta = models.CharField(max_length=100, null=True, blank=True, default='')
    total_venta = models.PositiveIntegerField(null=True, blank=True, default=0)
    
    def __str__(self):
        return f'Orden {self.numero_orden}'
    
class Venta_producto(models.Model):
    producto = models.ForeignKey(Prod_venta, on_delete=models.CASCADE, null=True, blank=True, default=0)
    cantidad = models.PositiveIntegerField(null=True, blank=True, default=0)
    id_orden = models.ForeignKey(Orden_venta, on_delete=models.CASCADE, null=True, blank=True, default=0)
    precio_producto = models.PositiveIntegerField(null=True, blank=True, default=0)
    def __str__(self):
        return f'Venta {self.id} - {self.producto}'
