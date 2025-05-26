from django.db import models
from users.models import CustomUser

class Project(models.Model):
    """User projects model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    tools_used = models.CharField(max_length=255)
    project_url = models.URLField(blank=True, null=True)
    project_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'projects_proyecto'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return self.title