from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Solicitud

def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard") 
        else:
            return render(request, "backoffice/login.html", {"error": "Credenciales inválidas"})
    
    return render(request, "backoffice/login.html")

@login_required
def dashboard(request):
    solicitudes_pendientes = Solicitud.objects.filter(estado='pendiente')
    solicitudes_aprobadas = Solicitud.objects.filter(estado='aprobado')
    solicitudes_rechazadas = Solicitud.objects.filter(estado='rechazado')

    return render(request, 'backoffice/dashboard.html', {
        'pendientes': solicitudes_pendientes,
        'aprobados': solicitudes_aprobadas,
        'rechazados': solicitudes_rechazadas,
    })



