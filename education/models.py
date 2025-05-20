from django.db import models
from users.models import CustomUser

class Education(models.Model):
    """User education model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'education_educacion'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return f"{self.degree} - {self.institution}"