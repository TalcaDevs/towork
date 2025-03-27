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
from .serializers import UserSerializer, SolicitudSerializer
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Solicitud
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

@extend_schema(
    tags=['authentication'],
    operation_id='signup',
    summary='Registrar nuevo usuario',
    description='Endpoint para registrar nuevos usuarios con nombre, apellido, email y contraseña.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string', 'example': 'Juan'},
                'last_name': {'type': 'string', 'example': 'Pérez'},
                'email': {'type': 'string', 'format': 'email', 'example': 'usuario@ejemplo.com'},
                'password': {'type': 'string', 'format': 'password', 'example': '********'}
            },
            'required': ['first_name', 'last_name', 'email', 'password']
        }
    },
    responses={
        201: OpenApiResponse(description='Usuario registrado exitosamente',
                          examples={
                              'application/json': {
                                  'message': 'Usuario registrado exitosamente',
                                  'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...',
                                  'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...'
                              }
                          }),
        400: OpenApiResponse(description='Error en los datos proporcionados')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registro_usuario(request):
    """
    Endpoint para registrar nuevos usuarios con nombre, apellido, email y contraseña.
    """
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")
    password = request.data.get("password")

    if not first_name or not last_name or not email or not password:
        return Response({"error": "Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "El correo ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=email,  # Usamos el email como username
        password=make_password(password)  # Encriptamos la contraseña
    )

    # Generamos tokens JWT para el usuario registrado
    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Usuario registrado exitosamente",
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=['authentication'],
    operation_id='signin',
    summary='Iniciar sesión de usuario',
    description='Endpoint para iniciar sesión con email y contraseña y obtener tokens JWT.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'example': 'usuario@ejemplo.com'},
                'password': {'type': 'string', 'format': 'password', 'example': '********'}
            },
            'required': ['email', 'password']
        }
    },
    responses={
        200: OpenApiResponse(description='Inicio de sesión exitoso', 
                          examples={
                              'application/json': {
                                  'message': 'Inicio de sesión exitoso',
                                  'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...',
                                  'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...'
                              }
                          }),
        401: OpenApiResponse(description='Credenciales inválidas')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_usuario(request):
    """
    Endpoint para iniciar sesión con email y contraseña y obtener tokens JWT.
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email y contraseña son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Inicio de sesión exitoso",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    tags=['users'],
    operation_id='save-profile',
    summary='Guardar perfil completo del usuario',
    description='Recibe toda la información del usuario (perfil, educación, experiencia, etc.) y la guarda en la base de datos.',
    responses={
        201: OpenApiResponse(description='Perfil guardado correctamente, solicitud en estado pendiente',
                         examples={
                             'application/json': {
                                 'message': 'Perfil guardado correctamente, solicitud en estado pendiente.'
                             }
                         }),
        400: OpenApiResponse(description='Error en los datos proporcionados')
    },
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string', 'example': 'Juan'},
                'last_name': {'type': 'string', 'example': 'Pérez'},
                'foto_perfil': {'type': 'string', 'format': 'uri', 'example': 'https://ejemplo.com/foto.jpg'},
                'descripcion': {'type': 'string', 'example': 'Desarrollador con 5 años de experiencia'},
                'telefono': {'type': 'string', 'example': '+123456789'},
                'ubicacion': {'type': 'string', 'example': 'Ciudad de México'},
                'linkedin': {'type': 'string', 'format': 'uri', 'example': 'https://linkedin.com/in/juanperez'},
                'id_portafolio_web': {'type': 'string', 'format': 'uri', 'example': 'https://portafolio.dev/juanperez'},
                'educacion': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'institucion': {'type': 'string', 'example': 'Universidad Ejemplo'},
                            'titulo': {'type': 'string', 'example': 'Ingeniería en Sistemas'},
                            'fecha_inicio': {'type': 'string', 'format': 'date', 'example': '2015-09-01'},
                            'fecha_fin': {'type': 'string', 'format': 'date', 'example': '2020-06-30'}
                        },
                        'required': ['institucion', 'titulo', 'fecha_inicio']
                    }
                },
                'experiencia': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'empresa': {'type': 'string', 'example': 'Empresa Ejemplo'},
                            'puesto': {'type': 'string', 'example': 'Desarrollador Senior'},
                            'descripcion': {'type': 'string', 'example': 'Desarrollo de aplicaciones web con Django y React'},
                            'fecha_inicio': {'type': 'string', 'format': 'date', 'example': '2020-07-01'},
                            'fecha_fin': {'type': 'string', 'format': 'date', 'example': '2023-01-15', 'nullable': True}
                        },
                        'required': ['empresa', 'puesto', 'fecha_inicio']
                    }
                },
                'certificaciones': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'nombre': {'type': 'string', 'example': 'Certificación Django'},
                            'institucion': {'type': 'string', 'example': 'Django Foundation'},
                            'fecha_obtencion': {'type': 'string', 'format': 'date', 'example': '2021-05-15'},
                            'url_certificado': {'type': 'string', 'format': 'uri', 'example': 'https://certificaciones.com/cert123'}
                        },
                        'required': ['nombre', 'institucion', 'fecha_obtencion']
                    }
                },
                'proyectos': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'titulo': {'type': 'string', 'example': 'Sistema de Gestión de Inventario'},
                            'descripcion': {'type': 'string', 'example': 'Aplicación web para gestionar inventario de productos con reportes y alertas'},
                            'herramientas_usadas': {'type': 'string', 'example': 'Django, React, Docker'},
                            'url_proyecto': {'type': 'string', 'format': 'uri', 'example': 'https://github.com/usuario/proyecto', 'nullable': True},
                            'imagen_proyecto': {'type': 'string', 'format': 'uri', 'example': 'https://ejemplo.com/captura.jpg', 'nullable': True}
                        },
                        'required': ['titulo', 'descripcion', 'herramientas_usadas']
                    }
                },
                'skills': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['Python', 'Django', 'React', 'JavaScript']
                },
                'idiomas': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'language': {
                                'type': 'object',
                                'properties': {
                                    'nombre': {'type': 'string', 'example': 'Inglés'}
                                },
                                'required': ['nombre']
                            },
                            'nivel': {'type': 'string', 'enum': ['Básico', 'Intermedio', 'Avanzado', 'Nativo'], 'example': 'Avanzado'}
                        },
                        'required': ['language', 'nivel']
                    }
                }
            }
        }
    }
)
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
    Educacion.objects.filter(usuario=user).delete()
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
    ExperienciaLaboral.objects.filter(usuario=user).delete()
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
    Certificacion.objects.filter(usuario=user).delete()
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
    Proyecto.objects.filter(usuario=user).delete()
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

    # 6️⃣ Guardar Skills sin duplicados
    UserSkill.objects.filter(usuario=user).delete()
    skills_data = request.data.get("skills", [])
    for skill_name in skills_data:
        skill, _ = Skill.objects.get_or_create(nombre=skill_name)
        user_skill, created = UserSkill.objects.get_or_create(usuario=user, skill=skill)

    # 7️⃣ Guardar Idiomas
    UserLanguage.objects.filter(usuario=user).delete()
    idiomas_data = request.data.get("idiomas", [])
    for idioma in idiomas_data:
        nombre_idioma = idioma.get("language", {}).get("nombre")
        if not nombre_idioma:
            continue  # Evita errores si no hay nombre

        language, _ = Language.objects.get_or_create(nombre=nombre_idioma)
        
        user_language, created = UserLanguage.objects.get_or_create(
            usuario=user,
            language=language,
            defaults={"nivel": idioma["nivel"]}  # Solo se guarda si no existe
        )
        if not created:
            user_language.nivel = idioma["nivel"]  # Si ya existe, actualiza el nivel
            user_language.save()

    solicitud, created = Solicitud.objects.get_or_create(
        usuario=user,
        estado="pendiente",
        defaults={"descripcion": "Solicitud de revisión de perfil completa."}
    )

    if not created:
        solicitud.descripcion = "Solicitud de revisión de perfil actualizada."
        solicitud.estado = "pendiente"
        solicitud.save()

    return Response({"message": "Perfil guardado correctamente, solicitud en estado 'pendiente'."}, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=['users'],
    operation_id='get-profile',
    summary='Obtener perfil completo del usuario',
    description='Obtiene toda la información del usuario autenticado (perfil, educación, experiencia, etc.).',
    responses={
        200: UserSerializer
    }
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def obtener_perfil_completo(request):
    """
    Obtiene toda la información del usuario autenticado (perfil, educación, experiencia, etc.).
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=['backoffice'],
    operation_id='list-users',
    summary='Listar todos los usuarios',
    description='Obtiene la lista de usuarios con toda su información (educación, experiencia, skills, etc.).',
    responses={
        200: UserSerializer(many=True)
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def obtener_usuarios(request):
    """
    Obtiene la lista de usuarios con toda su información (educación, experiencia, skills, etc.).
    """
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=['backoffice'],
    operation_id='list-requests',
    summary='Listar solicitudes',
    description='Lista todas las solicitudes de usuarios, permitiendo filtrar por estado.',
    parameters=[
        OpenApiParameter(name='estado', description='Filtrar por estado (pendiente, aceptada, rechazada)', required=False, type=str, enum=['pendiente', 'aceptada', 'rechazada'])
    ],
    responses={
        200: SolicitudSerializer(many=True)
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def listar_solicitudes(request):
    """
    Lista todas las solicitudes de usuarios, permitiendo filtrar por estado.
    Parámetros opcionales:
        - estado: pendiente, aceptada, rechazada
    """
    estado = request.GET.get('estado')  # Obtiene el estado de la URL (si se proporciona)

    if estado:
        solicitudes = Solicitud.objects.filter(estado=estado)
    else:
        solicitudes = Solicitud.objects.all()

    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)