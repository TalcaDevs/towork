from django.db import models
from users.models import CustomUser

class Language(models.Model):
    """Language model"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'languages_language'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return self.name

class UserLanguage(models.Model):
    """User-language relationship"""
    LEVEL_CHOICES = [
        ('Básico', 'Básico'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
        ('Nativo', 'Nativo'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="languages")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    
    class Meta:
        db_table = 'languages_userlanguage'  # Mantiene el nombre original de la tabla
        unique_together = ('user', 'language')

    def __str__(self):
        return f"{self.user} - {self.language.name} ({self.level})"