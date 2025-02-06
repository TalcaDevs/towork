from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
        ('moderador', 'Moderador'),
    )

    """Modelo para usuarios o estudiantes egresados."""
    foto_perfil = models.URLField(blank=True, null=True)
    descripcion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    id_portafolio_web = models.URLField(blank=True, null=True)

    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Solicitud(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.estado}'