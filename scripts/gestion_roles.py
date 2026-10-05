#!/usr/bin/env python3
"""
Programa para gestionar roles de usuarios (Superusuario, Profesor, Estudiante)
y registrar estudiantes automáticamente
"""
import os
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError
from apps.core.models import PerfilUsuario, Curso

print("=" * 70)
print("👥 GESTIÓN DE ROLES Y ESTUDIANTES")
print("=" * 70)

# ============================================
# 1. CREAR PERFILES PARA USUARIOS EXISTENTES
# ============================================
print("\n📝 1. CREANDO PERFILES PARA USUARIOS EXISTENTES")

usuarios = User.objects.all()
perfiles_creados = 0

for usuario in usuarios:
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={
            'rol': 'SUPERUSUARIO' if usuario.is_superuser else 'ESTUDIANTE',
            'identificacion': f"ID-{usuario.id:06d}",
            'fecha_registro': datetime.now(),
        }
    )
    if created:
        perfiles_creados += 1
        print(f"  ✅ Perfil creado para: {usuario.username} - {perfil.get_rol_display()}")

print(f"✅ {perfiles_creados} perfiles creados")

# ============================================
# 2. FUNCIÓN PARA REGISTRAR ESTUDIANTES
# ============================================
def registrar_estudiante(username, email, password, first_name='', last_name='', identificacion=''):
    """Registra un nuevo estudiante con su perfil"""
    try:
        # Crear usuario
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario {username} ya existe")
            return None
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Crear perfil
        perfil = PerfilUsuario.objects.create(
            usuario=user,
            rol='ESTUDIANTE',
            identificacion=identificacion or f"EST-{user.id:06d}",
            fecha_registro=datetime.now(),
        )
        
        print(f"✅ Estudiante registrado: {username} ({first_name} {last_name})")
        return user
        
    except Exception as e:
        print(f"❌ Error al registrar {username}: {e}")
        return None

# ============================================
# 3. REGISTRAR ESTUDIANTES MASIVOS
# ============================================
print("\n📚 3. REGISTRANDO ESTUDIANTES DE EJEMPLO")

estudiantes_data = [
    {
        'username': 'estudiante_001',
        'email': 'estudiante001@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'María',
        'last_name': 'García',
        'identificacion': 'EST-001'
    },
    {
        'username': 'estudiante_002',
        'email': 'estudiante002@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Carlos',
        'last_name': 'López',
        'identificacion': 'EST-002'
    },
    {
        'username': 'estudiante_003',
        'email': 'estudiante003@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'identificacion': 'EST-003'
    },
    {
        'username': 'estudiante_004',
        'email': 'estudiante004@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'identificacion': 'EST-004'
    },
    {
        'username': 'estudiante_005',
        'email': 'estudiante005@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Laura',
        'last_name': 'Rodríguez',
        'identificacion': 'EST-005'
    },
]

estudiantes_registrados = 0
for data in estudiantes_data:
    user = registrar_estudiante(**data)
    if user:
        estudiantes_registrados += 1

print(f"\n✅ {estudiantes_registrados} estudiantes registrados")

# ============================================
# 4. CREAR PROFESORES
# ============================================
print("\n👨‍🏫 4. REGISTRANDO PROFESORES")

profesores_data = [
    {
        'username': 'profesor_001',
        'email': 'profesor001@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Roberto',
        'last_name': 'Sánchez',
    },
    {
        'username': 'profesor_002',
        'email': 'profesor002@edunomad.com',
        'password': 'EduNomad2024',
        'first_name': 'Elena',
        'last_name': 'Fernández',
    },
]

def registrar_profesor(username, email, password, first_name='', last_name=''):
    """Registra un profesor con su perfil"""
    try:
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario {username} ya existe")
            return None
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Marcar como staff (profesor)
        user.is_staff = True
        user.save()
        
        # Crear perfil
        perfil = PerfilUsuario.objects.create(
            usuario=user,
            rol='PROFESOR',
            identificacion=f"PROF-{user.id:06d}",
            fecha_registro=datetime.now(),
        )
        
        print(f"✅ Profesor registrado: {username} ({first_name} {last_name})")
        return user
        
    except Exception as e:
        print(f"❌ Error al registrar profesor {username}: {e}")
        return None

profesores_registrados = 0
for data in profesores_data:
    user = registrar_profesor(**data)
    if user:
        profesores_registrados += 1

print(f"\n✅ {profesores_registrados} profesores registrados")

# ============================================
# 5. ASIGNAR PROFESORES A CURSOS
# ============================================
print("\n📚 5. ASIGNANDO PROFESORES A CURSOS")

cursos = Curso.objects.all()[:10]  # Tomar 10 cursos

profesores = PerfilUsuario.objects.filter(rol='PROFESOR')

if profesores.exists() and cursos.exists():
    for curso in cursos:
        profesor = random.choice(profesores)
        curso.profesores.add(profesor.usuario)
        print(f"  ✅ Profesor {profesor.usuario.username} asignado a: {curso.titulo[:40]}")
else:
    print("  ⚠️ No hay profesores o cursos disponibles para asignar")

# ============================================
# 6. ESTADÍSTICAS
# ============================================
print("\n📊 6. ESTADÍSTICAS DE USUARIOS Y ROLES")

total_usuarios = User.objects.count()
total_profesores = PerfilUsuario.objects.filter(rol='PROFESOR').count()
total_estudiantes = PerfilUsuario.objects.filter(rol='ESTUDIANTE').count()
total_superusuarios = PerfilUsuario.objects.filter(rol='SUPERUSUARIO').count()

print(f"  👤 Total usuarios: {total_usuarios}")
print(f"  👨‍🏫 Profesores: {total_profesores}")
print(f"  👨‍🎓 Estudiantes: {total_estudiantes}")
print(f"  👑 Superusuarios: {total_superusuarios}")

print("\n📋 DETALLE DE USUARIOS:")
for perfil in PerfilUsuario.objects.all():
    rol_icon = {
        'SUPERUSUARIO': '👑',
        'PROFESOR': '👨‍🏫',
        'ESTUDIANTE': '👨‍🎓',
        'ADMIN': '👤',
    }.get(perfil.rol, '👤')
    
    cursos_count = perfil.cursos_inscritos.count() if perfil.es_estudiante else 0
    print(f"  {rol_icon} {perfil.usuario.username:20} | {perfil.get_rol_display():12} | {perfil.nombre_completo:25} | {cursos_count} cursos")

# ============================================
# 7. FUNCIÓN PARA CREAR ESTUDIANTE DESDE CONSOLA
# ============================================
print("\n" + "=" * 70)
print("💡 COMANDO PARA REGISTRAR ESTUDIANTE DESDE CONSOLA:")
print("=" * 70)
print("""
python manage.py shell -c "
from gestion_roles import registrar_estudiante
registrar_estudiante('nombre_usuario', 'email@dominio.com', 'contraseña', 'Nombre', 'Apellido')
"
""")

print("\n" + "=" * 70)
print("✅ ¡GESTIÓN DE ROLES COMPLETADA!")
print("=" * 70)
