from rest_framework import serializers
from .models import CustomUser, Request
from education.models import Education
from experience.models import WorkExperience
from certifications.models import Certification
from projects.models import Project
from skills.models import Skill, UserSkill
from languages.models import Language, UserLanguage
from .models import Template

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'start_date', 'end_date']

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'description', 'start_date', 'end_date']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['name', 'institution', 'date_obtained', 'certificate_url']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tools_used', 'project_url', 'project_image']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']

class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = UserSkill
        fields = ['skill']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']

class UserLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = UserLanguage
        fields = ['language', 'level']

class UserSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True)
    experience = WorkExperienceSerializer(many=True, source='work_experience')
    certifications = CertificationSerializer(many=True)
    projects = ProjectSerializer(many=True)
    skills = UserSkillSerializer(many=True)
    languages = UserLanguageSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'profile_photo', 
            'description', 'phone', 'location', 'linkedin', 'portfolio_url', 
            'education', 'experience', 'certifications', 'projects', 
            'skills', 'languages', 'template',
            'terms_accepted', 'terms_accepted_date'
        ]

class RequestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Request
        fields = ['id', 'user', 'description', 'status', 'created_date']