#!/usr/bin/env python3
"""
Script único para crear TODOS los modelos y datos del LMS
"""
import os
import random
import hashlib
import time
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.db import models

print("🚀 CONFIGURACIÓN COMPLETA DEL LMS")
print("=" * 70)

# ============================================
# 1. IMPORTAR MODELOS
# ============================================
print("\n📦 1. Importando modelos...")

from apps.core.models import Curso, RecursoEducativo
from apps.language_practice.models import Course, Lesson

print("✅ Modelos importados correctamente")

# ============================================
# 2. SINCRONIZAR CURSOS (core -> language_practice)
# ============================================
print("\n🔄 2. Sincronizando cursos...")

cursos_core = Curso.objects.all()
print(f"📚 Cursos en core: {cursos_core.count()}")

cursos_sincronizados = 0
for curso_core in cursos_core:
    # Buscar o crear curso en language_practice
    course_lp, created = Course.objects.get_or_create(
        title=curso_core.titulo,
        defaults={
            'description': curso_core.descripcion or f"Curso de {curso_core.categoria}",
            'language': curso_core.categoria.lower(),
            'level': curso_core.nivel.lower() if curso_core.nivel else 'intermediate',
            'is_active': True,
        }
    )
    if created:
        cursos_sincronizados += 1
        print(f"  ✅ Curso LP creado: {course_lp.title}")

print(f"✅ {cursos_sincronizados} cursos sincronizados")
print(f"📊 Total cursos en language_practice: {Course.objects.count()}")

# ============================================
# 3. CREAR USUARIOS DE PRUEBA
# ============================================
print("\n👤 3. Creando usuarios de prueba...")

usuarios_creados = 0
for i in range(5):
    username = f"estudiante_{i+1}"
    email = f"estudiante{i+1}@edunomad.com"
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=email,
            password="EduNomad2024"
        )
        user.first_name = f"Estudiante {i+1}"
        user.last_name = f"Apellido {i+1}"
        user.save()
        usuarios_creados += 1

print(f"✅ {usuarios_creados} usuarios creados")
print(f"📊 Total usuarios: {User.objects.count()}")

# ============================================
# 4. CREAR LECCIONES PARA CADA CURSO (usando language_practice)
# ============================================
print("\n📖 4. Creando lecciones para cursos...")

cursos_lp = Course.objects.all()
print(f"📚 Cursos LP disponibles: {cursos_lp.count()}")

if cursos_lp.count() == 0:
    print("❌ No hay cursos en language_practice. Ejecuta primero la sincronización.")
    exit()

temas_leccion = [
    "Introducción", "Conceptos Básicos", "Fundamentos", "Estructura",
    "Análisis", "Práctica", "Ejercicios", "Evaluación",
    "Aplicación", "Proyecto", "Caso de Estudio", "Profundización"
]

lecciones_creadas = 0
for curso_lp in cursos_lp:
    # Seleccionar temas aleatorios (5-8 por curso)
    temas_seleccionados = random.sample(temas_leccion, min(8, len(temas_leccion)))
    
    for i, tema in enumerate(temas_seleccionados[:random.randint(5, 8)], 1):
        leccion, created = Lesson.objects.get_or_create(
            course=curso_lp,
            title=f"{tema} - {curso_lp.title[:30]}",
            defaults={'order': i}
        )
        if created:
            lecciones_creadas += 1

print(f"✅ {lecciones_creadas} lecciones creadas")
print(f"📊 Total lecciones: {Lesson.objects.count()}")

# ============================================
# 5. GENERAR ESTADÍSTICAS
# ============================================
print("\n📊 5. ESTADÍSTICAS FINALES:")
print("=" * 50)
print(f"  👤 Usuarios: {User.objects.count()}")
print(f"  📚 Recursos: {RecursoEducativo.objects.count()}")
print(f"  🎓 Cursos (core): {Curso.objects.count()}")
print(f"  🎓 Cursos (language_practice): {Course.objects.count()}")
print(f"  📖 Lecciones: {Lesson.objects.count()}")

print("\n" + "=" * 50)
print("✅ ¡CONFIGURACIÓN COMPLETA!")
print("📝 Ejecuta: python manage.py runserver")
