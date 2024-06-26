from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


"""
    Extensión del modelo AbstractUser de Django para gestionar usuarios con campos adicionales.

    Campos adicionales:
    - telefono: CharField, máximo 20 caracteres. Almacena el número de teléfono del usuario.
    - direccion: CharField, máximo 255 caracteres. Almacena la dirección del usuario.
    - profile_image: ImageField, opcional. Almacena la imagen de perfil del usuario.
    
    Relaciones:
    - groups:  Permite asociar usuarios a uno o más grupos.
    - user_permissions:  Permite asignar permisos específicos a usuarios.

    Atributos heredados de AbstractUser disponibles:
    - username: Nombre de usuario.
    - first_name: Primer nombre del usuario.
    - last_name: Apellido del usuario.
    - email: Correo electrónico del usuario.
    - password: Contraseña del usuario.
    - is_active: Booleano que indica si el usuario está activo.
    - is_staff: Booleano que indica si el usuario tiene acceso al panel de administración.
    - date_joined: Fecha en la que el usuario se unió al sistema.
"""
class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
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
     
        

