from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
        ('moderador', 'Moderador'),
    )

    foto_perfil = models.URLField(blank=True, null=True)
    descripcion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    id_portafolio_web = models.URLField(blank=True, null=True)

    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Solicitud(models.Model):
    ESTADOS = (
        ('nuevo', 'Nuevo Usuario'),
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='nuevo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.estado}'


class SolicitudLog(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='logs')
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    estado_anterior = models.CharField(max_length=20)
    nuevo_estado = models.CharField(max_length=20)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} cambió {self.solicitud} de {self.estado_anterior} a {self.nuevo_estado} el {self.fecha_cambio}'


class UserDeletionLog(models.Model):
    deleted_user_id = models.IntegerField()
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='deletion_logs')
    deletion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        deleted_by_info = f"User ID {self.deleted_by.id}" if self.deleted_by else "Unknown"
        return f"User ID {self.deleted_user_id} deleted by {deleted_by_info} on {self.deletion_date}'"


class Template(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
