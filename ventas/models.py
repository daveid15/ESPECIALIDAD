from django.db import models
from django.contrib.auth.models import Group, User 


class Cliente(models.Model):
    cliente_name = models.CharField(max_length=100, null=True, blank=True)
    cliente_last_name = models.CharField(max_length=100, null=True, blank=True)
   
    def get_nombre_cliente_completo(self):
        return f'{self.cliente_name} {self.cliente_last_name}'

    def __str__(self):
        return self.get_nombre_cliente_completo()


class Prod_venta(models.Model):
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    agregados = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.producto}'
    

    
#Orden de Compra
class Orden_venta(models.Model):
    numero_orden = models.AutoField(primary_key=True)
    cliente_orden = models.CharField(max_length=100)
    producto_orden = models.CharField(max_length=100)
    cantidad_orden = models.CharField(max_length=100)
    monto_orden = models.PositiveIntegerField(default=0)
    agregados_orden = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f' {self.numero_orden}'