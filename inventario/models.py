from django.db import models
from django.contrib.auth.models import Group, User 

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