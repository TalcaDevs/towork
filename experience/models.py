from django.db import models
from users.models import CustomUser

class WorkExperience(models.Model):
    """User work experience model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="work_experience")
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'experience_experiencialaboral'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return f"{self.position} at {self.company}"