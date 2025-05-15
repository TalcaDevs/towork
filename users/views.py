from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser
from education.models import Education
from experience.models import WorkExperience
from projects.models import Project
from certifications.models import Certification
from skills.models import Skill, UserSkill
from languages.models import Language, UserLanguage
from .serializers import UserSerializer, RequestSerializer
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Request, Template
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

@extend_schema(
    tags=['authentication'],
    operation_id='signup',
    summary='Register new user',
    description='Endpoint for registering new users with name, last name, email and password.',
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
        201: OpenApiResponse(description='User registered successfully',
                          examples={
                              'application/json': {
                                  'message': 'Usuario registrado exitosamente',
                                  'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...',
                                  'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...'
                              }
                          }),
        400: OpenApiResponse(description='Error in provided data')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):

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
        username=email,  
        password=make_password(password) 
    )

    Request.objects.create(
        user=user,
        description="Usuario recién registrado",
        status="new"
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Usuario registrado exitosamente",
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=['authentication'],
    operation_id='signin',
    summary='User login',
    description='Endpoint for user login with email and password to obtain JWT tokens.',
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
        200: OpenApiResponse(description='Login successful', 
                          examples={
                              'application/json': {
                                  'message': 'Inicio de sesión exitoso',
                                  'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...',
                                  'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...'
                              }
                          }),
        401: OpenApiResponse(description='Invalid credentials')
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
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
    summary='Save complete user profile',
    description='Receives all user information (profile, education, experience, etc.) and saves it to the database.',
    responses={
        201: OpenApiResponse(description='Profile saved correctly, request in pending status',
                         examples={
                             'application/json': {
                                 'message': 'Perfil guardado correctamente, solicitud en estado pendiente.'
                             }
                         }),
        400: OpenApiResponse(description='Error in provided data')
    },
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string', 'example': 'Juan'},
                'last_name': {'type': 'string', 'example': 'Pérez'},
                'profile_photo': {'type': 'string', 'format': 'uri', 'example': 'https://ejemplo.com/foto.jpg'},
                'description': {'type': 'string', 'example': 'Desarrollador con 5 años de experiencia'},
                'phone': {'type': 'string', 'example': '+123456789'},
                'location': {'type': 'string', 'example': 'Ciudad de México'},
                'linkedin': {'type': 'string', 'format': 'uri', 'example': 'https://linkedin.com/in/juanperez'},
                'portfolio_url': {'type': 'string', 'format': 'uri', 'example': 'https://portafolio.dev/juanperez'},
                'education': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'institution': {'type': 'string', 'example': 'Universidad Ejemplo'},
                            'degree': {'type': 'string', 'example': 'Ingeniería en Sistemas'},
                            'start_date': {'type': 'string', 'format': 'date', 'example': '2015-09-01'},
                            'end_date': {'type': 'string', 'format': 'date', 'example': '2020-06-30'}
                        },
                        'required': ['institution', 'degree', 'start_date']
                    }
                },
                'experience': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'company': {'type': 'string', 'example': 'Empresa Ejemplo'},
                            'position': {'type': 'string', 'example': 'Desarrollador Senior'},
                            'description': {'type': 'string', 'example': 'Desarrollo de aplicaciones web con Django y React'},
                            'start_date': {'type': 'string', 'format': 'date', 'example': '2020-07-01'},
                            'end_date': {'type': 'string', 'format': 'date', 'example': '2023-01-15', 'nullable': True}
                        },
                        'required': ['company', 'position', 'start_date']
                    }
                },
                'certifications': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'example': 'Certificación Django'},
                            'institution': {'type': 'string', 'example': 'Django Foundation'},
                            'date_obtained': {'type': 'string', 'format': 'date', 'example': '2021-05-15'},
                            'certificate_url': {'type': 'string', 'format': 'uri', 'example': 'https://certificaciones.com/cert123'}
                        },
                        'required': ['name', 'institution', 'date_obtained']
                    }
                },
                'projects': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string', 'example': 'Sistema de Gestión de Inventario'},
                            'description': {'type': 'string', 'example': 'Aplicación web para gestionar inventario de productos con reportes y alertas'},
                            'tools_used': {'type': 'string', 'example': 'Django, React, Docker'},
                            'project_url': {'type': 'string', 'format': 'uri', 'example': 'https://github.com/usuario/proyecto', 'nullable': True},
                            'project_image': {'type': 'string', 'format': 'uri', 'example': 'https://ejemplo.com/captura.jpg', 'nullable': True}
                        },
                        'required': ['title', 'description', 'tools_used']
                    }
                },
                'skills': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['Python', 'Django', 'React', 'JavaScript']
                },
                'languages': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'language': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string', 'example': 'Inglés'}
                                },
                                'required': ['name']
                            },
                            'level': {'type': 'string', 'enum': ['Básico', 'Intermedio', 'Avanzado', 'Nativo'], 'example': 'Avanzado'}
                        },
                        'required': ['language', 'level']
                    }
                },
                'template': {'type': 'integer', 'example': 1, 'description': 'ID of the template to assign to the user'
                }
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_complete_profile(request):

    user = request.user 

    # 1️⃣ Save basic user data
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.profile_photo = request.data.get("profile_photo", user.profile_photo)
    user.description = request.data.get("description", user.description)
    user.phone = request.data.get("phone", user.phone)
    user.location = request.data.get("location", user.location)
    user.linkedin = request.data.get("linkedin", user.linkedin)
    user.portfolio_url = request.data.get("portfolio_url", user.portfolio_url)
    
    # Add template processing
    template_id = request.data.get("template")
    if template_id is not None:
        try:
            template_obj = Template.objects.get(pk=template_id)
            user.template = template_obj
        except Template.DoesNotExist:
            # More specific error handling
            return Response(
                {"error": f"The template with ID {template_id} does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    user.save()

    # 2️⃣ Save Education
    Education.objects.filter(user=user).delete()
    education_data = request.data.get("education", [])
    for edu in education_data:
        Education.objects.create(
            user=user,
            institution=edu["institution"],
            degree=edu["degree"],
            start_date=edu["start_date"],
            end_date=edu.get("end_date"),
        )

    # 3️⃣ Save Work Experience
    WorkExperience.objects.filter(user=user).delete()
    experience_data = request.data.get("experience", [])
    for exp in experience_data:
        WorkExperience.objects.create(
            user=user,
            company=exp["company"],
            position=exp["position"],
            description=exp.get("description", ""),
            start_date=exp["start_date"],
            end_date=exp.get("end_date"),
        )

    # 4️⃣ Save Certifications
    Certification.objects.filter(user=user).delete()
    certifications_data = request.data.get("certifications", [])
    for cert in certifications_data:
        Certification.objects.create(
            user=user,
            name=cert["name"],
            institution=cert["institution"],
            date_obtained=cert["date_obtained"],
            certificate_url=cert.get("certificate_url", ""),
        )

    # 5️⃣ Save Projects
    Project.objects.filter(user=user).delete()
    projects_data = request.data.get("projects", [])
    for proj in projects_data:
        Project.objects.create(
            user=user,
            title=proj["title"],
            description=proj["description"],
            tools_used=proj["tools_used"],
            project_url=proj.get("project_url", ""),
            project_image=proj.get("project_image", ""),
        )

    # 6️⃣ Save Skills without duplicates
    UserSkill.objects.filter(user=user).delete()
    skills_data = request.data.get("skills", [])
    for skill_name in skills_data:
        skill, _ = Skill.objects.get_or_create(name=skill_name)
        user_skill, created = UserSkill.objects.get_or_create(user=user, skill=skill)

    # 7️⃣ Save Languages
    UserLanguage.objects.filter(user=user).delete()
    languages_data = request.data.get("languages", [])
    for lang in languages_data:
        language_name = lang.get("language", {}).get("name")
        if not language_name:
            continue  

        language, _ = Language.objects.get_or_create(name=language_name)
        
        user_language, created = UserLanguage.objects.get_or_create(
            user=user,
            language=language,
            defaults={"level": lang["level"]} 
        )
        if not created:
            user_language.level = lang["level"]  
            user_language.save()

    request_obj, created = Request.objects.get_or_create(
        user=user,
        defaults={
            "description": "Solicitud de revisión de perfil completa.",
            "status": "pending"
        }
    )

    if not created:
        request_obj.description = "Solicitud de revisión de perfil actualizada."
        request_obj.status = "pending" 
        request_obj.save()

    return Response({"message": "Perfil guardado correctamente, solicitud en estado 'pendiente'."}, status=status.HTTP_201_CREATED)
    
@extend_schema(
    tags=['users'],
    operation_id='get-profile',
    summary='Get complete user profile',
    description='Gets all information of the authenticated user (profile, education, experience, etc.).',
    responses={
        200: UserSerializer
    }
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_complete_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=['backoffice'],
    operation_id='list-users',
    summary='List all users',
    description='Gets the list of users with all their information (education, experience, skills, etc.).',
    responses={
        200: UserSerializer(many=True)
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_users(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=['backoffice'],
    operation_id='list-requests',
    summary='List requests',
    description='Lists all user requests, allowing filtering by status.',
    parameters=[
        OpenApiParameter(name='status', description='Filter by status (pending, accepted, rejected)', required=False, type=str, enum=['pending', 'accepted', 'rejected'])
    ],
    responses={
        200: RequestSerializer(many=True)
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def list_requests(request):
    status_param = request.GET.get('status')  

    if status_param:
        requests = Request.objects.filter(status=status_param)
    else:
        requests = Request.objects.all()

    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)