from django.db import models
from users.models import CustomUser

# Create your models here.
class Language(models.Model):
    """Modelo de idiomas"""
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class UserLanguage(models.Model):
    """Relación usuario - idioma"""
    NIVEL_CHOICES = [
        ('Básico', 'Básico'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
        ('Nativo', 'Nativo'),
    ]

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="idiomas")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)

    class Meta:
        unique_together = ('usuario', 'language')

    def __str__(self):
        return f"{self.usuario} - {self.language.nombre} ({self.nivel})"
