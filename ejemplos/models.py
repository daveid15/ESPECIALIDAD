from django.contrib.auth.models import Group, User #importa los modelos Group y user
from django.db import models #importa los metodos necesarios para trabajar con modellos

class Habilidad(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre habilidad')
    nivel = models.IntegerField(null=True, blank=True, verbose_name='Nivel Poder')
    estado = models.CharField(max_length=100, null=True, blank=True, default='Activo', verbose_name='Estado')   
    created = models.DateTimeField(auto_now_add=True,verbose_name='Fecha Creación')
    updated = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualización')
    class Meta:
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        ordering = ['nombre']   
    def __str__(self):
        return self.name

class Heroe(models.Model):
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    nombe_heroe = models.CharField(max_length=100, null=True, blank=True)
    nacionalidad_heroe = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True, default='Activo')   
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Heroe'
        verbose_name_plural = 'Heroes'
        ordering = ['nombe_heroe']
    
    def __str__(self):
        return self.nombe_heroe

def custom_upload_to(instance, filename):
    return 'product/' + filename

class Product(models.Model):
    product_name = models.CharField(max_length=100, null=True, blank=True)
    product_price = models.IntegerField(null=True, blank=True)
    product_image = models.CharField(max_length=240, null=True, blank=True)
    product_state = models.CharField(max_length=100, null=True, blank=True, default='No')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['product_name']
    
    def __str__(self):
        return self.product_name

class Provider(models.Model):
    provider_name = models.CharField(max_length=100, null=True, blank=True)
    provider_last_name = models.CharField(max_length=240, null=True, blank=True)
    provider_mail = models.CharField(max_length=240, null=True, blank=True)
    provider_state = models.CharField(max_length=100, null=True, blank=True, default='Activo')

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        ordering = ['provider_name']
    
    def __str__(self):
        return self.provider_name

class Category(models.Model):
    category_name = models.CharField(max_length=100, null=True, blank=True)
    category_state = models.CharField(max_length=100, null=True, blank=True, default='Activa')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categorys'
        ordering = ['category_name']
    
    def __str__(self):
        return self.category_name
#ejemplo muchos a muchos
class Autor(models.Model):
    nombre = models.CharField(max_length = 240,null=True, blank=True)   
    created = models.DateTimeField(auto_now_add=True,verbose_name='Fecha Creación')
    updated = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualización')

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    autor = models.ManyToManyField(Autor) 
    nombre = models.CharField(max_length = 240,null=True, blank=True)   
    palabras_clave = models.CharField(max_length = 240,null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True,verbose_name='Fecha Creación')
    updated = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualización')

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

