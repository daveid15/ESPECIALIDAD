from django.db import models
from django.contrib.auth.models import Group, User 
from django.contrib.postgres.fields import ArrayField
from inventario.models import Product

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions import ExtractMonth
from django.db.models import Count

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class Proveedor(models.Model):
    proveedor_name = models.CharField(max_length=100, null=True, blank=True)
    proveedor_last_name = models.CharField(max_length=100, null=True, blank=True)
    proveedor_rut = models.CharField(max_length=100, null=True, blank=True)
    proveedor_mail = models.CharField(max_length=100, null=True, blank=True)
    proveedor_address = models.CharField(max_length=100, null=True, blank=True)
    proveedor_region = models.CharField(max_length=100, null=True, blank=True)
    proveedor_comuna = models.CharField(max_length=100, null=True, blank=True)
    proveedor_phone = models.CharField(max_length=100, null=True, blank=True)
    proveedor_insumo = ArrayField(models.CharField(max_length=100, null=True, blank=True))
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Campo de fecha de creación

    def get_nombre_completo(self):
        return f'{self.proveedor_name} {self.proveedor_last_name}'

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['proveedor_name']

    def __str__(self):
        return self.get_nombre_completo()
class Orden_compra(models.Model):
    proveedor_orden = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    
    ESTADOS_ORDEN = [
        ('enviado', 'Enviado'),
        ('rechazado', 'Rechazado'), 
        ('aceptado', 'Aceptado'),
        ('anulado', 'Anulado'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADOS_ORDEN, default='enviado')


class Producto_Orden(models.Model):
    orden_id = models.ForeignKey(Orden_compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad_orden = models.PositiveIntegerField()

