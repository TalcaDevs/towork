from django.db import models
from users.models import CustomUser

class Certificacion(models.Model):
    """Modelo de certificaciones"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="certificaciones")
    nombre = models.CharField(max_length=255)
    institucion = models.CharField(max_length=255)
    fecha_obtencion = models.DateField()
    url_certificado = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.institucion}"
