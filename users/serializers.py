from rest_framework import serializers
from .models import CustomUser
from education.models import Educacion
from experience.models import ExperienciaLaboral
from certifications.models import Certificacion
from projects.models import Proyecto
from skills.models import Skill, UserSkill
from languages.models import Language, UserLanguage
from .models import Solicitud
from .models import Template

class EducacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educacion
        fields = ['institucion', 'titulo', 'fecha_inicio', 'fecha_fin']

class ExperienciaLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienciaLaboral
        fields = ['empresa', 'puesto', 'descripcion', 'fecha_inicio', 'fecha_fin']

class CertificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificacion
        fields = ['nombre', 'institucion', 'fecha_obtencion', 'url_certificado']

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'herramientas_usadas', 'url_proyecto', 'imagen_proyecto']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['nombre']

class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = UserSkill
        fields = ['skill']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['nombre']

class UserLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = UserLanguage
        fields = ['language', 'nivel']

class UserSerializer(serializers.ModelSerializer):
    educacion = EducacionSerializer(many=True)
    experiencia = ExperienciaLaboralSerializer(many=True, source='experiencia_laboral')
    certificaciones = CertificacionSerializer(many=True)
    proyectos = ProyectoSerializer(many=True)
    skills = UserSkillSerializer(many=True)
    idiomas = UserLanguageSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'foto_perfil', 'descripcion', 'telefono', 
            'ubicacion', 'linkedin', 'id_portafolio_web', 'educacion', 'experiencia', 
            'certificaciones', 'proyectos', 'skills', 'idiomas', 'template'
        ]

class SolicitudSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()
    class Meta:
        model = Solicitud
        fields = ['id', 'usuario', 'descripcion', 'estado', 'fecha_creacion']
