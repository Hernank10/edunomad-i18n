#!/usr/bin/env python3
"""
Script para generar lecciones masivas para todos los cursos existentes
Usando el modelo Lesson de language_practice
"""
import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, RecursoEducativo
from apps.language_practice.models import Lesson, Course

print("📚 GENERANDO LECCIONES MASIVAS")
print("=" * 60)

# Obtener cursos de language_practice
cursos_lp = Course.objects.all()
print(f"🎓 Cursos en language_practice: {cursos_lp.count()}")

if cursos_lp.count() == 0:
    print("❌ No hay cursos en language_practice. Creando cursos...")
    # Crear cursos de ejemplo en language_practice
    from apps.core.models import Curso as CoreCurso
    
    for core_curso in CoreCurso.objects.all():
        curso_lp, created = Course.objects.get_or_create(
            title=core_curso.titulo,
            defaults={
                'description': core_curso.descripcion,
                'language': core_curso.categoria.lower(),
                'level': core_curso.nivel.lower() if core_curso.nivel else 'intermediate',
                'is_active': True,
            }
        )
        if created:
            print(f"  ✅ Curso LP creado: {curso_lp.title}")
    
    cursos_lp = Course.objects.all()
    print(f"✅ Total cursos LP: {cursos_lp.count()}")

# Temas para lecciones
temas = [
    "Conceptos Básicos", "Fundamentos", "Introducción", "Primeros Pasos",
    "Estructura", "Análisis", "Práctica", "Ejercicios", "Evaluación",
    "Aplicación", "Proyecto", "Caso de Estudio", "Profundización",
    "Técnicas Avanzadas", "Optimización", "Recursos Adicionales"
]

tipos_orden = list(range(1, 16))  # 1-15 para orden

print("\n🔄 Generando lecciones...")
lecciones_creadas = 0
errores = 0

for curso in cursos_lp:
    # Número aleatorio de lecciones por curso (3-10)
    num_lecciones = random.randint(3, 10)
    print(f"\n📖 Curso: {curso.title}")
    print(f"   Generando {num_lecciones} lecciones...")
    
    # Mezclar órdenes
    ordenes = random.sample(tipos_orden, min(num_lecciones, len(tipos_orden)))
    
    for i, orden in enumerate(ordenes[:num_lecciones], 1):
        try:
            # Seleccionar tema
            tema = random.choice(temas)
            
            # Generar título
            prefijos = ["Introducción a", "Fundamentos de", "Práctica de", "Evaluación de", "Aplicación de"]
            prefijo = random.choice(prefijos)
            titulo = f"{prefijo} {tema}"
            
            # Crear lección
            leccion = Lesson.objects.create(
                course=curso,
                title=titulo[:200],
                order=orden
            )
            
            lecciones_creadas += 1
            
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"   ❌ Error en lección {i}: {e}")

print("\n" + "=" * 60)
print(f"🎉 {lecciones_creadas} lecciones creadas exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")
print(f"📊 Total lecciones: {Lesson.objects.count()}")

# Mostrar resumen por curso
print("\n📋 RESUMEN POR CURSO:")
for curso in cursos_lp:
    count = Lesson.objects.filter(course=curso).count()
    print(f"  - {curso.title[:40]}: {count} lecciones")
