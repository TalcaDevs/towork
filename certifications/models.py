from django.db import models
from users.models import CustomUser

class Certification(models.Model):
    """Certification model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    date_obtained = models.DateField()
    certificate_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'certifications_certificacion'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return f"{self.name} - {self.institution}"