from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser
from education.models import Educacion
from experience.models import ExperienciaLaboral
from projects.models import Proyecto
from certifications.models import Certificacion
from skills.models import Skill, UserSkill
from languages.models import Language, UserLanguage

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def guardar_perfil_completo(request):
    """
    Recibe toda la información del usuario (perfil, educación, experiencia, etc.)
    y la guarda en la base de datos.
    """
    user = request.user  # Usuario autenticado

    # 1️⃣ Guardar datos básicos del usuario
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.foto_perfil = request.data.get("foto_perfil", user.foto_perfil)
    user.descripcion = request.data.get("descripcion", user.descripcion)
    user.telefono = request.data.get("telefono", user.telefono)
    user.ubicacion = request.data.get("ubicacion", user.ubicacion)
    user.linkedin = request.data.get("linkedin", user.linkedin)
    user.id_portafolio_web = request.data.get("id_portafolio_web", user.id_portafolio_web)
    user.save()

    # 2️⃣ Guardar Educación
    educacion_data = request.data.get("educacion", [])
    for edu in educacion_data:
        Educacion.objects.create(
            usuario=user,
            institucion=edu["institucion"],
            titulo=edu["titulo"],
            fecha_inicio=edu["fecha_inicio"],
            fecha_fin=edu.get("fecha_fin"),
        )

    # 3️⃣ Guardar Experiencia Laboral
    experiencia_data = request.data.get("experiencia", [])
    for exp in experiencia_data:
        ExperienciaLaboral.objects.create(
            usuario=user,
            empresa=exp["empresa"],
            puesto=exp["puesto"],
            descripcion=exp.get("descripcion", ""),
            fecha_inicio=exp["fecha_inicio"],
            fecha_fin=exp.get("fecha_fin"),
        )

    # 4️⃣ Guardar Certificaciones
    certificaciones_data = request.data.get("certificaciones", [])
    for cert in certificaciones_data:
        Certificacion.objects.create(
            usuario=user,
            nombre=cert["nombre"],
            institucion=cert["institucion"],
            fecha_obtencion=cert["fecha_obtencion"],
            url_certificado=cert.get("url_certificado", ""),
        )

    # 5️⃣ Guardar Proyectos
    proyectos_data = request.data.get("proyectos", [])
    for proy in proyectos_data:
        Proyecto.objects.create(
            usuario=user,
            titulo=proy["titulo"],
            descripcion=proy["descripcion"],
            herramientas_usadas=proy["herramientas_usadas"],
            url_proyecto=proy.get("url_proyecto", ""),
            imagen_proyecto=proy.get("imagen_proyecto", ""),
        )

    # 6️⃣ Guardar Skills
    skills_data = request.data.get("skills", [])
    for skill_name in skills_data:
        skill, created = Skill.objects.get_or_create(nombre=skill_name)
        UserSkill.objects.create(usuario=user, skill=skill)

    # 7️⃣ Guardar Idiomas
    idiomas_data = request.data.get("idiomas", [])
    for idioma in idiomas_data:
        language, created = Language.objects.get_or_create(nombre=idioma["nombre"])
        UserLanguage.objects.create(usuario=user, language=language, nivel=idioma["nivel"])

    return Response({"message": "Perfil guardado correctamente"}, status=status.HTTP_201_CREATED)
