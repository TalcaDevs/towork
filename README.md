```
Estructura de Carpetas del Proyecto ToWork
```
"To Work" es una plataforma web diseñada para estudiantes recién egresados que buscan posicionarse eficazmente en el mercado laboral.

```
📁 towork/
│
├── 📁 api/                   # Aplicación de API REST
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── schema.py           # Configuración de documentación API
│   ├── serializers.py      # Serializadores para la API
│   ├── tests.py
│   ├── urls.py             # Rutas de la API
│   └── views.py            # Vistas de la API
│
├── 📁 backoffice/            # Aplicación de administración
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py             # Rutas del panel de administración
│   └── views.py            # Vistas del panel de administración
│
├── 📁 certifications/        # Aplicación de certificaciones
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 education/             # Aplicación de educación
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 experience/            # Aplicación de experiencia laboral
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 languages/             # Aplicación de idiomas
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 likes/                 # Aplicación de likes/favoritos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 projects/              # Aplicación de proyectos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 skills/                # Aplicación de habilidades
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── 📁 static/                # Archivos estáticos
│   ├── css/
│   │   ├── approved.css
│   │   ├── dashboard.css
│   │   ├── detail.css
│   │   ├── global.css
│   │   ├── login.css
│   │   ├── mobile.css
│   │   ├── pagination.css
│   │   ├── pending.css
│   │   ├── popup.css
│   │   ├── rejected.css
│   │   └── variables.css
│   └── js/
│       ├── detail.js
│       ├── filter.js
│       ├── mobile.js
│       ├── navbar.js
│       └── pagination.js
│
├── 📁 templates/             # Plantillas HTML
│   └── backoffice/
│       ├── approved.html
│       ├── dashboard.html
│       ├── detail.html
│       ├── filter.html
│       ├── login.html
│       ├── navbar.html
│       ├── pending.html
│       ├── rejected.html
│       └── sidebar.html
│
├── 📁 towork/                # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # Rutas principales
│   └── wsgi.py
│
├── 📁 users/                 # Aplicación de usuarios
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore                # Archivos ignorados por Git
└── manage.py                 # Script de administración de Django
```

ToWork - Plataforma Web para recién egresados
Estructura del Proyecto

Aplicaciones Core
```
towork: Directorio principal del proyecto que contiene la configuración global, incluyendo settings.py, urls.py y los archivos WSGI/ASGI para despliegue.
users: Gestiona los usuarios del sistema, extendiendo el modelo de usuario de Django (CustomUser) y las solicitudes (Solicitud). Incluye autenticación, registro y gestión del perfil completo.
backoffice: Implementa el panel administrativo donde los administradores pueden gestionar solicitudes y perfiles de usuarios.
api: Proporciona endpoints REST para la comunicación con aplicaciones cliente, usando Django REST Framework con JWT para autenticación.
```

Aplicaciones de Datos de Usuario
Cada una de estas aplicaciones maneja un aspecto específico del perfil del usuario:
```
education: Almacena información sobre la formación académica del usuario.
experience: Gestiona la experiencia laboral de los usuarios.
certifications: Contiene certificaciones obtenidas por los usuarios.
projects: Almacena los proyectos realizados por los usuarios.
skills: Maneja las habilidades técnicas de los usuarios.
languages: Gestiona los idiomas que conoce el usuario y su nivel de dominio.
likes: Sistema de favoritos o likes entre usuarios.
```

Recursos Estáticos y Plantillas
```
static: Contiene archivos CSS y JavaScript organizados por funcionalidad:

CSS para el diseño visual, separado en múltiples archivos para facilitar el mantenimiento.
JavaScript para interacciones en el cliente, filtrado, paginación y adaptación móvil.
```

templates: Almacena las plantillas HTML del sistema, principalmente para el backoffice, con vistas para:
```
Solicitudes pendientes, aprobadas y rechazadas
Vista detallada de perfiles
Panel de control (dashboard)
Inicio de sesión
Componentes reutilizables (sidebar, navbar)
```


Características Principales
```
Autenticación JWT: Sistema de autenticación basado en tokens JWT para la API.
Documentación API: Integrada con drf-spectacular para generar documentación OpenAPI (Swagger/Redoc).
Perfil Completo: Los usuarios pueden registrar información detallada sobre su experiencia, educación, proyectos, etc.
Panel Administrativo: Interfaz para gestionar solicitudes con vistas específicas para pendientes, aprobadas y rechazadas.
Diseño Responsive: Adaptado para dispositivos móviles y escritorio.
Registro de Cambios: Sistema de logs para mantener registro de cambios en solicitudes.
```

Tecnologías Utilizadas
```
Backend: Django y Django REST Framework
Base de datos: MySQL
Autenticación: JWT (JSON Web Tokens)
Frontend: Vite/React
Documentación API: drf-spectacular
```

Requisitos
```
Python 3.8+
MySQL
Librerías de Python listadas en requirements.txt
```

Configuración
```
Crea un entorno virtual de Python
Instala las dependencias: pip install -r requirements.txt
Configura el archivo .env con los parámetros de tu base de datos
Aplica las migraciones: python manage.py migrate
Crea un superusuario: python manage.py createsuperuser
Inicia el servidor: python manage.py runserver
```

Acceso al Panel
```
Backoffice: http://localhost:8000/backoffice/
API Docs: http://localhost:8000/api/docs/
```
