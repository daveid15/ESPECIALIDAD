from django.db import models
from django.contrib.auth.models import Group, User 
from django.contrib.postgres.fields import ArrayField
from inventario.models import Product

class Proveedor(models.Model):
    proveedor_name = models.CharField(max_length=100, null=True, blank=True)
    proveedor_last_name = models.CharField(max_length=100, null=True, blank=True)
    proveedor_rut = models.CharField(max_length=100, null=True, blank=True)
    proveedor_mail = models.CharField(max_length=100, null=True, blank=True)
    proveedor_address = models.CharField(max_length=100, null=True, blank=True)
    proveedor_region = models.CharField(max_length=100, null=True, blank=True)
    proveedor_comuna = models.CharField(max_length=100, null=True, blank=True)
    proveedor_phone = models.CharField(max_length=100, null=True, blank=True)
    proveedor_insumo = ArrayField(models.CharField(max_length=100,null=True, blank=True))

    def get_nombre_completo(self):
        return f'{self.proveedor_name} {self.proveedor_last_name}'

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['proveedor_name']

    def __str__(self):
        return self.get_nombre_completo()


'''
class OrdenCompra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)
    # Otros campos que necesites

    def __str__(self):
        return f'Orden de compra {self.id}'
        '''

'''
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    
    def __str__(self):
        return f'{self.nombre}'
        '''
    
'''
    
class Producto_orden(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    '''
    

    
#Orden de Compra
class Orden_compra(models.Model):
    proveedor_orden = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto_orden = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad_orden = models.PositiveIntegerField()
    
    ESTADOS_ORDEN = [
        ('enviado', 'Enviado'),
        ('rechazado', 'Rechazado'),
        ('aceptado', 'Aceptado'),
        ('anulado', 'Anulado'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADOS_ORDEN, default='enviado')
    
    '''
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_creacion = models.DateField(auto_now_add=True)
    id_orden = models.CharField(max_length=30)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Orden de compra {self.id}'
    
    '''
    