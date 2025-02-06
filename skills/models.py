from django.db import models
from users.models import CustomUser

# Create your models here.
class Skill(models.Model):
    """Modelo de habilidades (Skills)"""
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class UserSkill(models.Model):
    """Relación usuario - skill"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'skill')
