#!/usr/bin/env python3
"""
Script para generar prácticas y evaluaciones con ejercicios interactivos
"""
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, Practica, Evaluacion, EjercicioInteractivo

try:
    from apps.language_practice.models import Lesson, Course
except:
    Lesson = None
    Course = None
    print("⚠️ Language Practice no disponible")

print("📚 GENERANDO PRÁCTICAS Y EVALUACIONES")
print("=" * 60)

# Obtener cursos
cursos = Curso.objects.all()
print(f"🎓 Cursos encontrados: {cursos.count()}")

# Temas para ejercicios
temas = [
    "Conceptos Básicos", "Fundamentos", "Estructura", "Análisis",
    "Aplicación", "Práctica", "Evaluación", "Proyecto"
]

def generar_preguntas_opcion_multiple(tema, cantidad=3):
    preguntas = []
    for i in range(cantidad):
        preguntas.append({
            'tipo': 'OPCION_MULTIPLE',
            'pregunta': f'¿Cuál es el concepto principal de {tema}? (Pregunta {i+1})',
            'opciones': [
                f'Opción A - Concepto sobre {tema}',
                f'Opción B - Concepto relacionado con {tema}',
                f'Opción C - Concepto avanzado de {tema}',
                f'Opción D - Concepto básico de {tema}'
            ],
            'respuesta_correcta': f'Opción A - Concepto sobre {tema}',
            'explicacion': f'El concepto principal de {tema} es...',
            'puntaje': 5
        })
    return preguntas

def generar_preguntas_verdadero_falso(tema, cantidad=3):
    preguntas = []
    for i in range(cantidad):
        preguntas.append({
            'tipo': 'VERDADERO_FALSO',
            'pregunta': f'¿Es correcto afirmar que {tema} es fundamental? (Pregunta {i+1})',
            'opciones': ['Verdadero', 'Falso'],
            'respuesta_correcta': 'Verdadero',
            'explicacion': f'{tema} es fundamental porque...',
            'puntaje': 3
        })
    return preguntas

practicas_creadas = 0
evaluaciones_creadas = 0
ejercicios_creados = 0

for curso in cursos:
    print(f"\n📖 Curso: {curso.titulo}")
    
    # 1. Crear Prácticas
    num_practicas = random.randint(2, 4)
    for i in range(num_practicas):
        tema = random.choice(temas)
        practica = Practica.objects.create(
            curso=curso,
            titulo=f"Práctica {i+1}: {tema}",
            descripcion=f"Ejercicios prácticos sobre {tema} para el curso {curso.titulo}",
            tipo=random.choice(['EJERCICIO', 'QUIZ', 'REPASO']),
            puntaje_maximo=100,
            duracion_minutos=random.randint(10, 25),
            orden=i+1,
            is_active=True
        )
        practicas_creadas += 1
        
        # Crear ejercicios para la práctica
        num_ejercicios = random.randint(3, 5)
        preguntas = []
        for j in range(num_ejercicios):
            if j % 2 == 0:
                preguntas_data = generar_preguntas_opcion_multiple(tema, 1)
            else:
                preguntas_data = generar_preguntas_verdadero_falso(tema, 1)
            
            for p in preguntas_data:
                ejercicio = EjercicioInteractivo.objects.create(
                    practica=practica,
                    tipo=p['tipo'],
                    pregunta=p['pregunta'],
                    opciones=p['opciones'],
                    respuesta_correcta=p['respuesta_correcta'],
                    explicacion=p.get('explicacion', ''),
                    puntaje=p['puntaje'],
                    orden=j+1,
                    is_active=True
                )
                ejercicios_creados += 1
                preguntas.append(p)
        
        practica.preguntas = preguntas
        practica.save()
        print(f"  ✅ Práctica: {practica.titulo} ({num_ejercicios} ejercicios)")
    
    # 2. Crear Evaluaciones
    num_evaluaciones = random.randint(1, 3)
    for i in range(num_evaluaciones):
        tema = random.choice(temas)
        evaluacion = Evaluacion.objects.create(
            curso=curso,
            titulo=f"Evaluación {i+1}: {tema}",
            descripcion=f"Evaluación sobre {tema} para el curso {curso.titulo}",
            tipo=random.choice(['EXAMEN', 'PRACTICA', 'FINAL']),
            puntaje_maximo=100,
            duracion_minutos=random.randint(20, 45),
            nota_minima=random.randint(60, 70),
            fecha_limite=datetime.now() + timedelta(days=random.randint(3, 10)),
            is_active=True
        )
        evaluaciones_creadas += 1
        
        # Crear ejercicios para la evaluación
        num_ejercicios = random.randint(5, 8)
        preguntas = []
        for j in range(num_ejercicios):
            if j % 3 == 0:
                preguntas_data = generar_preguntas_opcion_multiple(tema, 1)
            else:
                preguntas_data = generar_preguntas_verdadero_falso(tema, 1)
            
            for p in preguntas_data:
                ejercicio = EjercicioInteractivo.objects.create(
                    evaluacion=evaluacion,
                    tipo=p['tipo'],
                    pregunta=p['pregunta'],
                    opciones=p['opciones'],
                    respuesta_correcta=p['respuesta_correcta'],
                    explicacion=p.get('explicacion', ''),
                    puntaje=p['puntaje'],
                    orden=j+1,
                    is_active=True
                )
                ejercicios_creados += 1
                preguntas.append(p)
        
        evaluacion.preguntas = preguntas
        evaluacion.save()
        print(f"  ✅ Evaluación: {evaluacion.titulo} ({num_ejercicios} ejercicios)")

print("\n" + "=" * 60)
print(f"🎉 RESULTADOS:")
print(f"  📝 Prácticas creadas: {practicas_creadas}")
print(f"  📝 Evaluaciones creadas: {evaluaciones_creadas}")
print(f"  📝 Ejercicios creados: {ejercicios_creados}")
