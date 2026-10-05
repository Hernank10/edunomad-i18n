#!/usr/bin/env python3
"""
Verificar usuarios, contraseñas y credenciales del sistema
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from apps.core.models import PerfilUsuario

print("=" * 70)
print("🔍 VERIFICACIÓN DE CREDENCIALES Y USUARIOS")
print("=" * 70)

# ============================================
# 1. LISTA COMPLETA DE USUARIOS
# ============================================
print("\n👥 1. LISTA DE USUARIOS REGISTRADOS")
print("-" * 50)

usuarios = User.objects.all()
print(f"Total: {usuarios.count()} usuarios\n")

for user in usuarios:
    perfil = PerfilUsuario.objects.filter(usuario=user).first()
    rol = perfil.get_rol_display() if perfil else 'Sin perfil'
    print(f"  👤 {user.username:25} | {rol:12} | {user.email}")
    print(f"     Nombre: {user.first_name} {user.last_name}")
    print(f"     Staff: {'✅' if user.is_staff else '❌'} | Superuser: {'✅' if user.is_superuser else '❌'}")
    print("")

# ============================================
# 2. VERIFICAR CONTRASEÑAS POR DEFECTO
# ============================================
print("\n🔑 2. VERIFICANDO CONTRASEÑAS POR DEFECTO")
print("-" * 50)

credenciales_defecto = {
    'profesorhernanacevedoM777': 'password123',
    'estudiante_1': 'EduNomad2024',
    'estudiante_2': 'EduNomad2024',
    'estudiante_3': 'EduNomad2024',
    'estudiante_4': 'EduNomad2024',
    'estudiante_5': 'EduNomad2024',
    'test_gamificacion': 'test123',
}

print("🔑 Credenciales por defecto para usuarios de prueba:")
for username, password in credenciales_defecto.items():
    user = User.objects.filter(username=username).first()
    if user:
        autenticado = authenticate(username=username, password=password)
        print(f"  {username:25} | Contraseña: {password:15} | {'✅ Válida' if autenticado else '❌ Inválida'}")
    else:
        print(f"  {username:25} | ❌ Usuario no encontrado")

# ============================================
# 3. GENERAR REPORTE DE CREDENCIALES
# ============================================
print("\n📋 3. REPORTE DE CREDENCIALES RECOMENDADAS")
print("-" * 50)

print("""
🔑 CREDENCIALES DE ACCESO:

👑 SUPERUSUARIOS:
   Usuario: profesorhernanacevedoM777
   Contraseña: password123
   Acceso: Control total del sistema

👨‍🏫 PROFESORES:
   Usuario: profesor_001
   Contraseña: EduNomad2024
   Acceso: Gestión de cursos y estudiantes

   Usuario: profesor_002
   Contraseña: EduNomad2024
   Acceso: Gestión de cursos y estudiantes

   Usuario: profesor_003
   Contraseña: EduNomad2024
   Acceso: Gestión de cursos y estudiantes

   Usuario: profesor_004
   Contraseña: EduNomad2024
   Acceso: Gestión de cursos y estudiantes

👨‍🎓 ESTUDIANTES:
   Usuario: estudiante_001
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_002
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_003
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_004
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_005
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_006
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_007
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos

   Usuario: estudiante_008
   Contraseña: EduNomad2024
   Acceso: Cursos inscritos
""")

print("=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 70)
