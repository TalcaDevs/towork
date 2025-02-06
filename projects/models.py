from django.db import models
from users.models import CustomUser

# Create your models here.
class Proyecto(models.Model):
    """Modelo de proyectos de los usuarios"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="proyectos")
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    herramientas_usadas = models.CharField(max_length=255)
    url_proyecto = models.URLField(blank=True, null=True)
    imagen_proyecto = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

