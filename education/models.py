from django.db import models
from users.models import CustomUser

# Create your models here.
class Educacion(models.Model):
    """Modelo de educación de los usuarios"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="educacion")
    institucion = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.institucion}"
