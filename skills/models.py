from django.db import models
from users.models import CustomUser

class Skill(models.Model):
    """Skills model"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'skills_skill'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    """User-skill relationship"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'skills_userskill'  # Mantiene el nombre original de la tabla
        unique_together = ('user', 'skill')