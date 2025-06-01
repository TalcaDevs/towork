"""
Utilidades para sincronizar datos entre tablas privadas y públicas
"""
from django.db import transaction
from django.utils import timezone
from .models import (
    CustomUser, UserPublicProfile,
    PublicEducation, PublicWorkExperience, PublicCertification, 
    PublicProject, PublicSkill, PublicUserSkill, 
    PublicLanguage, PublicUserLanguage
)
from education.models import Education
from experience.models import WorkExperience
from certifications.models import Certification
from projects.models import Project
from skills.models import UserSkill
from languages.models import UserLanguage
import logging

logger = logging.getLogger(__name__)


@transaction.atomic
def sync_user_to_public_profile(user_id):
    """
    Sincroniza todos los datos de un usuario desde las tablas privadas 
    hacia las tablas públicas.
    
    Args:
        user_id (int): ID del usuario a sincronizar
        
    Returns:
        tuple: (success: bool, message: str, public_profile: UserPublicProfile|None)
    """
    try:
        # 1️⃣ Obtener el usuario
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return False, f"Usuario con ID {user_id} no existe", None
        
        logger.info(f"Iniciando sincronización para usuario: {user.username} (ID: {user_id})")
        
        # 2️⃣ Eliminar datos públicos existentes si existen
        existing_public_profile = UserPublicProfile.objects.filter(original_user_id=user_id).first()
        if existing_public_profile:
            logger.info(f"Eliminando perfil público existente para usuario {user_id}")
            existing_public_profile.delete()
        
        # 3️⃣ Crear nuevo perfil público
        template_name = user.template.name if user.template else None
        
        public_profile = UserPublicProfile.objects.create(
            original_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            profile_photo=user.profile_photo,
            description=user.description,
            phone=user.phone,
            location=user.location,
            linkedin=user.linkedin,
            portfolio_url=user.portfolio_url,
            role=user.role,
            terms_accepted=user.terms_accepted,
            terms_accepted_date=user.terms_accepted_date,
            template_name=template_name,
        )
        
        logger.info(f"Perfil público creado con ID: {public_profile.id}")
        
        # 4️⃣ Sincronizar Educación
        education_count = _sync_education(user, public_profile)
        
        # 5️⃣ Sincronizar Experiencia Laboral
        experience_count = _sync_work_experience(user, public_profile)
        
        # 6️⃣ Sincronizar Certificaciones
        certification_count = _sync_certifications(user, public_profile)
        
        # 7️⃣ Sincronizar Proyectos
        project_count = _sync_projects(user, public_profile)
        
        # 8️⃣ Sincronizar Habilidades
        skill_count = _sync_skills(user, public_profile)
        
        # 9️⃣ Sincronizar Idiomas
        language_count = _sync_languages(user, public_profile)
        
        # ✅ Log del resultado
        success_message = (
            f"Usuario {user.username} sincronizado exitosamente. "
            f"Datos copiados: {education_count} educaciones, {experience_count} experiencias, "
            f"{certification_count} certificaciones, {project_count} proyectos, "
            f"{skill_count} habilidades, {language_count} idiomas"
        )
        
        logger.info(success_message)
        return True, success_message, public_profile
        
    except Exception as e:
        error_message = f"Error sincronizando usuario {user_id}: {str(e)}"
        logger.error(error_message, exc_info=True)
        return False, error_message, None


def _sync_education(user, public_profile):
    """Sincroniza la educación del usuario"""
    education_list = Education.objects.filter(user=user)
    count = 0
    
    for edu in education_list:
        PublicEducation.objects.create(
            public_profile=public_profile,
            institution=edu.institution,
            degree=edu.degree,
            start_date=edu.start_date,
            end_date=edu.end_date,
        )
        count += 1
    
    logger.debug(f"Sincronizadas {count} educaciones")
    return count


def _sync_work_experience(user, public_profile):
    """Sincroniza la experiencia laboral del usuario"""
    experience_list = WorkExperience.objects.filter(user=user)
    count = 0
    
    for exp in experience_list:
        PublicWorkExperience.objects.create(
            public_profile=public_profile,
            company=exp.company,
            position=exp.position,
            description=exp.description,
            start_date=exp.start_date,
            end_date=exp.end_date,
        )
        count += 1
    
    logger.debug(f"Sincronizadas {count} experiencias laborales")
    return count


def _sync_certifications(user, public_profile):
    """Sincroniza las certificaciones del usuario"""
    certification_list = Certification.objects.filter(user=user)
    count = 0
    
    for cert in certification_list:
        PublicCertification.objects.create(
            public_profile=public_profile,
            name=cert.name,
            institution=cert.institution,
            date_obtained=cert.date_obtained,
            certificate_url=cert.certificate_url,
        )
        count += 1
    
    logger.debug(f"Sincronizadas {count} certificaciones")
    return count


def _sync_projects(user, public_profile):
    """Sincroniza los proyectos del usuario"""
    project_list = Project.objects.filter(user=user)
    count = 0
    
    for proj in project_list:
        PublicProject.objects.create(
            public_profile=public_profile,
            title=proj.title,
            description=proj.description,
            tools_used=proj.tools_used,
            project_url=proj.project_url,
            project_image=proj.project_image,
        )
        count += 1
    
    logger.debug(f"Sincronizados {count} proyectos")
    return count


def _sync_skills(user, public_profile):
    """Sincroniza las habilidades del usuario"""
    user_skills = UserSkill.objects.filter(user=user).select_related('skill')
    count = 0
    
    for user_skill in user_skills:
        # Crear o obtener la habilidad pública
        public_skill, created = PublicSkill.objects.get_or_create(
            name=user_skill.skill.name
        )
        
        # Crear la relación usuario-habilidad pública
        PublicUserSkill.objects.get_or_create(
            public_profile=public_profile,
            skill=public_skill
        )
        count += 1
    
    logger.debug(f"Sincronizadas {count} habilidades")
    return count


def _sync_languages(user, public_profile):
    """Sincroniza los idiomas del usuario"""
    user_languages = UserLanguage.objects.filter(user=user).select_related('language')
    count = 0
    
    for user_lang in user_languages:
        # Crear o obtener el idioma público
        public_language, created = PublicLanguage.objects.get_or_create(
            name=user_lang.language.name
        )
        
        # Crear la relación usuario-idioma pública
        PublicUserLanguage.objects.get_or_create(
            public_profile=public_profile,
            language=public_language,
            defaults={'level': user_lang.level}
        )
        count += 1
    
    logger.debug(f"Sincronizados {count} idiomas")
    return count


def delete_public_profile(user_id):
    """
    Elimina el perfil público de un usuario
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        public_profile = UserPublicProfile.objects.filter(original_user_id=user_id).first()
        
        if public_profile:
            username = public_profile.username
            public_profile.delete()
            message = f"Perfil público de {username} eliminado exitosamente"
            logger.info(message)
            return True, message
        else:
            message = f"No existe perfil público para usuario {user_id}"
            logger.warning(message)
            return True, message
            
    except Exception as e:
        error_message = f"Error eliminando perfil público de usuario {user_id}: {str(e)}"
        logger.error(error_message, exc_info=True)
        return False, error_message


def get_public_profile_stats():
    """
    Obtiene estadísticas de los perfiles públicos
    
    Returns:
        dict: Estadísticas de perfiles públicos
    """
    try:
        total_profiles = UserPublicProfile.objects.count()
        total_education = PublicEducation.objects.count()
        total_experience = PublicWorkExperience.objects.count()
        total_certifications = PublicCertification.objects.count()
        total_projects = PublicProject.objects.count()
        total_skills = PublicUserSkill.objects.count()
        total_languages = PublicUserLanguage.objects.count()
        
        return {
            'total_profiles': total_profiles,
            'total_education': total_education,
            'total_experience': total_experience,
            'total_certifications': total_certifications,
            'total_projects': total_projects,
            'total_skills': total_skills,
            'total_languages': total_languages,
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas públicas: {str(e)}")
        return {}