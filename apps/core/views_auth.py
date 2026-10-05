"""
Vistas de autenticación para EduNomad
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Curso, RecursoEducativo

def register_view(request):
    """Vista de registro de usuario"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'lms/auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'lms/auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado')
            return render(request, 'lms/auth/register.html')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Iniciar sesión automáticamente
        login(request, user)
        messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada.')
        return redirect('dashboard_estudiante')
    
    return render(request, 'lms/auth/register.html')

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard_estudiante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configurar sesión persistente
            if not remember:
                request.session.set_expiry(0)  # Cerrar al cerrar navegador
            else:
                request.session.set_expiry(1209600)  # 2 semanas
            
            messages.success(request, f'¡Bienvenido de vuelta {user.username}!')
            
            # Redirigir a la página anterior o dashboard
            next_url = request.GET.get('next', 'dashboard_estudiante')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'lms/auth/login.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

@login_required
def perfil_view(request):
    """Vista del perfil de usuario"""
    if request.method == 'POST':
        # Actualizar perfil
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Cambiar contraseña
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            messages.success(request, 'Contraseña actualizada correctamente')
            # Re-autenticar después de cambiar contraseña
            login(request, user)
        elif new_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('perfil')
        
        user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('perfil')
    
    return render(request, 'lms/auth/perfil.html', {'user': request.user})

@login_required
def dashboard_estudiante(request):
    """Dashboard del estudiante"""
    user = request.user
    cursos = Curso.objects.all().order_by('-fecha_creacion')[:6]
    
    # Calcular estadísticas
    total_cursos = Curso.objects.count()
    total_recursos = RecursoEducativo.objects.count()
    
    context = {
        'user': user,
        'total_cursos': total_cursos,
        'total_recursos': total_recursos,
        'cursos_inscritos': 0,  # TODO: Implementar inscripción
        'certificados': 0,  # TODO: Implementar certificados
        'cursos': cursos,  # Para mostrar en el dashboard
        'ultimos_cursos': cursos,
    }
    return render(request, 'lms/estudiante/dashboard.html', context)
