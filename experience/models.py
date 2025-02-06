from django.db import models
from users.models import CustomUser

# Create your models here.
class ExperienciaLaboral(models.Model):
    """Modelo de experiencia laboral de los usuarios"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="experiencia_laboral")
    empresa = models.CharField(max_length=255)
    puesto = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.puesto} en {self.empresa}"
