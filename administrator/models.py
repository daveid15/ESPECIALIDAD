from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    # Otros campos personalizados que necesites

    # Definir accesos inversos personalizados
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuarios'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuarios'
    )

    def __str__(self):
        return self.username
        
        

