"""
Serializers para datos públicos - Solo información aprobada
"""
from rest_framework import serializers
from .models import (
    UserPublicProfile, PublicEducation, PublicWorkExperience,
    PublicCertification, PublicProject, PublicSkill, PublicUserSkill,
    PublicLanguage, PublicUserLanguage
)


class PublicEducationSerializer(serializers.ModelSerializer):
    """Serializer para educación pública"""
    class Meta:
        model = PublicEducation
        fields = ['id', 'institution', 'degree', 'start_date', 'end_date', 'created_at']


class PublicWorkExperienceSerializer(serializers.ModelSerializer):
    """Serializer para experiencia laboral pública"""
    class Meta:
        model = PublicWorkExperience
        fields = ['id', 'company', 'position', 'description', 'start_date', 'end_date', 'created_at']


class PublicCertificationSerializer(serializers.ModelSerializer):
    """Serializer para certificaciones públicas"""
    class Meta:
        model = PublicCertification
        fields = ['id', 'name', 'institution', 'date_obtained', 'certificate_url', 'created_at']


class PublicProjectSerializer(serializers.ModelSerializer):
    """Serializer para proyectos públicos"""
    class Meta:
        model = PublicProject
        fields = ['id', 'title', 'description', 'tools_used', 'project_url', 'project_image', 'created_at']


class PublicSkillSerializer(serializers.ModelSerializer):
    """Serializer para habilidades públicas"""
    class Meta:
        model = PublicSkill
        fields = ['id', 'name']


class PublicUserSkillSerializer(serializers.ModelSerializer):
    """Serializer para relación usuario-habilidad pública"""
    skill = PublicSkillSerializer(read_only=True)

    class Meta:
        model = PublicUserSkill
        fields = ['skill']


class PublicLanguageSerializer(serializers.ModelSerializer):
    """Serializer para idiomas públicos"""
    class Meta:
        model = PublicLanguage
        fields = ['id', 'name']


class PublicUserLanguageSerializer(serializers.ModelSerializer):
    """Serializer para relación usuario-idioma pública"""
    language = PublicLanguageSerializer(read_only=True)

    class Meta:
        model = PublicUserLanguage
        fields = ['language', 'level']


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer completo para perfil público del usuario
    Incluye todas las entidades relacionadas
    """
    education = PublicEducationSerializer(many=True, read_only=True)
    work_experience = PublicWorkExperienceSerializer(many=True, read_only=True)
    certifications = PublicCertificationSerializer(many=True, read_only=True)
    projects = PublicProjectSerializer(many=True, read_only=True)
    skills = PublicUserSkillSerializer(many=True, read_only=True)
    languages = PublicUserLanguageSerializer(many=True, read_only=True)

    class Meta:
        model = UserPublicProfile
        fields = [
            # Información básica
            'id',
            'original_user_id',
            'username',
            'first_name',
            'last_name',
            'email',
            
            # Información del perfil
            'profile_photo',
            'description',
            'phone',
            'location',
            'linkedin',
            'portfolio_url',
            'role',
            'template_name',
            
            # Términos y condiciones
            'terms_accepted',
            'terms_accepted_date',
            
            # Entidades relacionadas
            'education',
            'work_experience',
            'certifications',
            'projects',
            'skills',
            'languages',
            
            # Metadatos
            'published_at',
            'last_updated',
        ]


class UserPublicProfileSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para perfil público - Solo información básica
    Útil para listados o búsquedas
    """
    skills_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    experience_years = serializers.SerializerMethodField()

    class Meta:
        model = UserPublicProfile
        fields = [
            'id',
            'original_user_id',
            'first_name',
            'last_name',
            'profile_photo',
            'description',
            'location',
            'linkedin',
            'portfolio_url',
            'role',
            'template_name',
            'skills_count',
            'projects_count',
            'experience_years',
            'published_at',
        ]

    def get_skills_count(self, obj):
        """Cuenta las habilidades del usuario"""
        return obj.skills.count()

    def get_projects_count(self, obj):
        """Cuenta los proyectos del usuario"""
        return obj.projects.count()

    def get_experience_years(self, obj):
        """Calcula los años de experiencia aproximados"""
        try:
            from datetime import date
            from dateutil.relativedelta import relativedelta
            
            experiences = obj.work_experience.all()
            if not experiences:
                return 0
            
            total_months = 0
            for exp in experiences:
                end_date = exp.end_date or date.today()
                delta = relativedelta(end_date, exp.start_date)
                total_months += delta.years * 12 + delta.months
            
            return round(total_months / 12, 1)
        except:
            return 0


class PublicProfileStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas generales de perfiles públicos
    """
    total_profiles = serializers.IntegerField()
    total_education = serializers.IntegerField()
    total_experience = serializers.IntegerField()
    total_certifications = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    total_languages = serializers.IntegerField()
    last_updated = serializers.DateTimeField()

    def to_representation(self, instance):
        """Agregar timestamp de cuando se generaron las estadísticas"""
        from datetime import datetime
        data = super().to_representation(instance)
        data['generated_at'] = datetime.now()
        return data