from django.db import models
from users.models import CustomUser

# Create your models here.
class Like(models.Model):
    """Modelo de likes o favoritos"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes_recibidos")
    liked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes_dados")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'liked_by')

    def __str__(self):
        return f"{self.liked_by} → {self.usuario}"

