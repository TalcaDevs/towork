from django.db import models
from users.models import CustomUser

class Like(models.Model):
    """Like or favorite model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_likes")
    liked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="given_likes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes_like'  # Mantiene el nombre original de la tabla
        unique_together = ('user', 'liked_by')

    def __str__(self):
        return f"{self.liked_by} → {self.user}"