from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('user', 'Usuario'),
        ('moderator', 'Moderador'),
    )

    profile_photo = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    
    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'users_customuser'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Request(models.Model):
    STATUSES = (
        ('new', 'Nuevo Usuario'),
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUSES, default='new')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_solicitud'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return f'{self.user.username} - {self.status}'

class RequestLog(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    change_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_solicitudlog'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return f'{self.user.username} changed {self.request} from {self.previous_status} to {self.new_status} on {self.change_date}'

class UserDeletionLog(models.Model):
    deleted_user_id = models.IntegerField()
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='deletion_logs')
    deletion_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_userdeletionlog'  # Mantiene el nombre original de la tabla

    def __str__(self):
        deleted_by_info = f"User ID {self.deleted_by.id}" if self.deleted_by else "Unknown"
        return f"User ID {self.deleted_user_id} deleted by {deleted_by_info} on {self.deletion_date}"

class Template(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'users_template'  # Mantiene el nombre original de la tabla

    def __str__(self):
        return self.name