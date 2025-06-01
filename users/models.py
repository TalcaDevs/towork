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


# ===== MODELOS PÚBLICOS (DATOS APROBADOS) =====

class UserPublicProfile(models.Model):
    """Perfil público del usuario - Solo datos aprobados"""
    ROLES = (
        ('admin', 'Administrador'),
        ('user', 'Usuario'),
        ('moderator', 'Moderador'),
    )

    # Trazabilidad (sin relación FK)
    original_user_id = models.IntegerField(help_text="ID del usuario original en CustomUser")
    
    # Datos básicos del usuario (copiados)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    
    # Datos del perfil (copiados)
    profile_photo = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    
    # Template (copiamos solo el nombre, no la relación)
    template_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadatos
    published_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_userpublicprofile'
        indexes = [
            models.Index(fields=['original_user_id']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Public)"


class PublicEducation(models.Model):
    """Educación pública - Solo datos aprobados"""
    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_publiceducation'

    def __str__(self):
        return f"{self.degree} - {self.institution} (Public)"


class PublicWorkExperience(models.Model):
    """Experiencia laboral pública - Solo datos aprobados"""
    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="work_experience")
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_publicworkexperience'

    def __str__(self):
        return f"{self.position} at {self.company} (Public)"


class PublicCertification(models.Model):
    """Certificaciones públicas - Solo datos aprobados"""
    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    date_obtained = models.DateField()
    certificate_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_publiccertification'

    def __str__(self):
        return f"{self.name} - {self.institution} (Public)"


class PublicProject(models.Model):
    """Proyectos públicos - Solo datos aprobados"""
    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    tools_used = models.CharField(max_length=255)
    project_url = models.URLField(blank=True, null=True)
    project_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_publicproject'

    def __str__(self):
        return f"{self.title} (Public)"


class PublicSkill(models.Model):
    """Habilidades públicas - Solo datos aprobados"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'users_publicskill'

    def __str__(self):
        return f"{self.name} (Public)"


class PublicUserSkill(models.Model):
    """Relación usuario-habilidad pública - Solo datos aprobados"""
    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(PublicSkill, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'users_publicuserskill'
        unique_together = ('public_profile', 'skill')

    def __str__(self):
        return f"{self.public_profile.first_name} - {self.skill.name} (Public)"


class PublicLanguage(models.Model):
    """Idiomas públicos - Solo datos aprobados"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'users_publiclanguage'

    def __str__(self):
        return f"{self.name} (Public)"


class PublicUserLanguage(models.Model):
    """Relación usuario-idioma pública - Solo datos aprobados"""
    LEVEL_CHOICES = [
        ('Básico', 'Básico'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
        ('Nativo', 'Nativo'),
    ]

    public_profile = models.ForeignKey(UserPublicProfile, on_delete=models.CASCADE, related_name="languages")
    language = models.ForeignKey(PublicLanguage, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    
    class Meta:
        db_table = 'users_publicuserlanguage'
        unique_together = ('public_profile', 'language')

    def __str__(self):
        return f"{self.public_profile.first_name} - {self.language.name} ({self.level}) (Public)"


# ===== MODELOS ORIGINALES (SIN CAMBIOS) =====

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
        db_table = 'users_solicitud'

    def __str__(self):
        return f'{self.user.username} - {self.status}'


class RequestLog(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    change_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_solicitudlog'

    def __str__(self):
        return f'{self.user.username} changed {self.request} from {self.previous_status} to {self.new_status} on {self.change_date}'


class UserDeletionLog(models.Model):
    deleted_user_id = models.IntegerField()
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='deletion_logs')
    deletion_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users_userdeletionlog'

    def __str__(self):
        deleted_by_info = f"User ID {self.deleted_by.id}" if self.deleted_by else "Unknown"
        return f"User ID {self.deleted_user_id} deleted by {deleted_by_info} on {self.deletion_date}"


class Template(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'users_template'

    def __str__(self):
        return self.name