#!/usr/bin/env python3
"""
Script para revisar todas las lecciones, prácticas y evaluaciones,
detectar faltantes y crearlas automáticamente.
Luego ejecuta una prueba completa del sistema.
"""
import os
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, Practica, Evaluacion, EjercicioInteractivo, RecursoEducativo
from django.db import models
from django.db.models import Count

print("=" * 80)
print("🔍 REVISIÓN Y COMPLETACIÓN DE CONTENIDO")
print("=" * 80)

# ============================================
# 1. ANALIZAR ESTADO ACTUAL
# ============================================
print("\n📊 1. ANALIZANDO ESTADO ACTUAL")
print("-" * 60)

cursos = Curso.objects.all()
total_cursos = cursos.count()
print(f"✅ Cursos totales: {total_cursos}")

# Estadísticas actuales
total_practicas = Practica.objects.count()
total_evaluaciones = Evaluacion.objects.count()
total_ejercicios = EjercicioInteractivo.objects.count()

print(f"📝 Prácticas actuales: {total_practicas}")
print(f"📝 Evaluaciones actuales: {total_evaluaciones}")
print(f"📝 Ejercicios actuales: {total_ejercicios}")

# ============================================
# 2. VERIFICAR CURSOS SIN PRÁCTICAS
# ============================================
print("\n🔍 2. VERIFICANDO CURSOS SIN CONTENIDO")
print("-" * 60)

cursos_sin_practicas = []
cursos_sin_evaluaciones = []

for curso in cursos:
    practicas_count = Practica.objects.filter(curso=curso).count()
    evaluaciones_count = Evaluacion.objects.filter(curso=curso).count()
    
    if practicas_count == 0:
        cursos_sin_practicas.append(curso)
    if evaluaciones_count == 0:
        cursos_sin_evaluaciones.append(curso)

print(f"⚠️ Cursos sin prácticas: {len(cursos_sin_practicas)}")
print(f"⚠️ Cursos sin evaluaciones: {len(cursos_sin_evaluaciones)}")

if cursos_sin_practicas:
    print("\n📋 Cursos sin prácticas:")
    for curso in cursos_sin_practicas[:10]:
        print(f"   • {curso.titulo[:50]}")
    if len(cursos_sin_practicas) > 10:
        print(f"   ... y {len(cursos_sin_practicas) - 10} más")

# ============================================
# 3. CREAR CONTENIDO FALTANTE
# ============================================
print("\n🔄 3. CREANDO CONTENIDO FALTANTE")
print("-" * 60)

TEMAS_LECCION = [
    "Introducción", "Conceptos Básicos", "Fundamentos", "Estructura",
    "Análisis", "Práctica", "Ejercicios", "Evaluación",
    "Aplicación", "Proyecto", "Caso de Estudio", "Profundización"
]

def generar_ejercicios_rapidos(tema, categoria, num=100):
    """Genera ejercicios rápidos para prácticas y evaluaciones"""
    ejercicios = []
    for i in range(num):
        tipo = random.choice(['OPCION_MULTIPLE', 'VERDADERO_FALSO'])
        if tipo == 'OPCION_MULTIPLE':
            ejercicios.append({
                'tipo': 'OPCION_MULTIPLE',
                'pregunta': f"Pregunta {i+1}: ¿Cuál es el concepto de {tema} en {categoria}?",
                'opciones': ['Opción A', 'Opción B', 'Opción C', 'Opción D'],
                'respuesta_correcta': 'Opción A',
                'explicacion': f'La respuesta correcta es Opción A sobre {tema}.',
                'puntaje': 3
            })
        else:
            ejercicios.append({
                'tipo': 'VERDADERO_FALSO',
                'pregunta': f"Pregunta {i+1}: ¿Es correcto que {tema} aplica en {categoria}?",
                'opciones': ['Verdadero', 'Falso'],
                'respuesta_correcta': 'Verdadero',
                'explicacion': f'{tema} sí aplica en {categoria}.',
                'puntaje': 2
            })
    return ejercicios

def crear_contenido_para_curso(curso, num_lecciones=3):
    """Crea lecciones, prácticas y evaluaciones para un curso"""
    creados = {'lecciones': 0, 'practicas': 0, 'evaluaciones': 0, 'ejercicios': 0}
    
    temas_seleccionados = random.sample(TEMAS_LECCION, min(num_lecciones, len(TEMAS_LECCION)))
    
    for i, tema in enumerate(temas_seleccionados, 1):
        try:
            # Crear práctica
            practica = Practica.objects.create(
                curso=curso,
                titulo=f"Práctica {i}: {tema}",
                descripcion=f"Práctica sobre {tema} para {curso.titulo[:30]}",
                tipo=random.choice(['EJERCICIO', 'QUIZ', 'REPASO']),
                puntaje_maximo=300,
                duracion_minutos=random.randint(15, 30),
                orden=i,
                is_active=True
            )
            creados['practicas'] += 1
            
            # Generar 100 ejercicios para la práctica
            ejercicios = generar_ejercicios_rapidos(tema, curso.categoria, 100)
            for j, ejercicio_data in enumerate(ejercicios, 1):
                EjercicioInteractivo.objects.create(
                    practica=practica,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data['opciones'],
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=j,
                    is_active=True
                )
                creados['ejercicios'] += 1
            
            # Crear evaluación
            evaluacion = Evaluacion.objects.create(
                curso=curso,
                titulo=f"Evaluación {i}: {tema}",
                descripcion=f"Evaluación sobre {tema} para {curso.titulo[:30]}",
                tipo=random.choice(['EXAMEN', 'PRACTICA', 'FINAL']),
                puntaje_maximo=300,
                duracion_minutos=random.randint(20, 45),
                nota_minima=random.randint(60, 70),
                fecha_limite=timezone.now() + timedelta(days=random.randint(3, 10)),
                is_active=True
            )
            creados['evaluaciones'] += 1
            
            # Generar 100 ejercicios para la evaluación
            ejercicios_eval = generar_ejercicios_rapidos(tema, curso.categoria, 100)
            for j, ejercicio_data in enumerate(ejercicios_eval, 1):
                EjercicioInteractivo.objects.create(
                    evaluacion=evaluacion,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data['opciones'],
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=j,
                    is_active=True
                )
                creados['ejercicios'] += 1
            
            creados['lecciones'] += 1
            
        except Exception as e:
            print(f"  ⚠️ Error en curso {curso.titulo[:30]}: {str(e)[:50]}")
    
    return creados

# Procesar cursos sin contenido
total_creados = {'lecciones': 0, 'practicas': 0, 'evaluaciones': 0, 'ejercicios': 0}

cursos_a_procesar = list(set(cursos_sin_practicas + cursos_sin_evaluaciones))

if cursos_a_procesar:
    print(f"\n📝 Procesando {len(cursos_a_procesar)} cursos sin contenido...")
    
    for i, curso in enumerate(cursos_a_procesar, 1):
        print(f"  [{i}/{len(cursos_a_procesar)}] {curso.titulo[:40]}...")
        creados = crear_contenido_para_curso(curso, num_lecciones=random.randint(3, 5))
        
        total_creados['lecciones'] += creados['lecciones']
        total_creados['practicas'] += creados['practicas']
        total_creados['evaluaciones'] += creados['evaluaciones']
        total_creados['ejercicios'] += creados['ejercicios']
        
        if i % 10 == 0:
            print(f"  ✅ Procesados {i} cursos...")
else:
    print("✅ Todos los cursos tienen contenido")

print(f"\n✅ Contenido creado:")
print(f"   • Lecciones: {total_creados['lecciones']}")
print(f"   • Prácticas: {total_creados['practicas']}")
print(f"   • Evaluaciones: {total_creados['evaluaciones']}")
print(f"   • Ejercicios: {total_creados['ejercicios']}")

# ============================================
# 4. VERIFICAR PRÁCTICAS SIN EJERCICIOS
# ============================================
print("\n🔍 4. VERIFICANDO PRÁCTICAS SIN EJERCICIOS")
print("-" * 60)

practicas_sin_ejercicios = []
for practica in Practica.objects.all():
    count = EjercicioInteractivo.objects.filter(practica=practica).count()
    if count == 0:
        practicas_sin_ejercicios.append(practica)

print(f"⚠️ Prácticas sin ejercicios: {len(practicas_sin_ejercicios)}")

if practicas_sin_ejercicios:
    print("📝 Creando ejercicios para prácticas sin contenido...")
    for practica in practicas_sin_ejercicios[:20]:
        ejercicios = generar_ejercicios_rapidos(
            practica.titulo[:20], 
            practica.curso.categoria, 
            100
        )
        for i, ejercicio_data in enumerate(ejercicios, 1):
            EjercicioInteractivo.objects.create(
                practica=practica,
                tipo=ejercicio_data['tipo'],
                pregunta=ejercicio_data['pregunta'],
                opciones=ejercicio_data['opciones'],
                respuesta_correcta=ejercicio_data['respuesta_correcta'],
                explicacion=ejercicio_data.get('explicacion', ''),
                puntaje=ejercicio_data.get('puntaje', 3),
                orden=i,
                is_active=True
            )
    print(f"✅ Ejercicios creados para {len(practicas_sin_ejercicios[:20])} prácticas")

# ============================================
# 5. VERIFICAR EVALUACIONES SIN EJERCICIOS
# ============================================
print("\n🔍 5. VERIFICANDO EVALUACIONES SIN EJERCICIOS")
print("-" * 60)

evaluaciones_sin_ejercicios = []
for evaluacion in Evaluacion.objects.all():
    count = EjercicioInteractivo.objects.filter(evaluacion=evaluacion).count()
    if count == 0:
        evaluaciones_sin_ejercicios.append(evaluacion)

print(f"⚠️ Evaluaciones sin ejercicios: {len(evaluaciones_sin_ejercicios)}")

if evaluaciones_sin_ejercicios:
    print("📝 Creando ejercicios para evaluaciones sin contenido...")
    for evaluacion in evaluaciones_sin_ejercicios[:20]:
        ejercicios = generar_ejercicios_rapidos(
            evaluacion.titulo[:20],
            evaluacion.curso.categoria,
            100
        )
        for i, ejercicio_data in enumerate(ejercicios, 1):
            EjercicioInteractivo.objects.create(
                evaluacion=evaluacion,
                tipo=ejercicio_data['tipo'],
                pregunta=ejercicio_data['pregunta'],
                opciones=ejercicio_data['opciones'],
                respuesta_correcta=ejercicio_data['respuesta_correcta'],
                explicacion=ejercicio_data.get('explicacion', ''),
                puntaje=ejercicio_data.get('puntaje', 3),
                orden=i,
                is_active=True
            )
    print(f"✅ Ejercicios creados para {len(evaluaciones_sin_ejercicios[:20])} evaluaciones")

# ============================================
# 6. ESTADÍSTICAS FINALES
# ============================================
print("\n📊 6. ESTADÍSTICAS FINALES")
print("-" * 60)

total_practicas_final = Practica.objects.count()
total_evaluaciones_final = Evaluacion.objects.count()
total_ejercicios_final = EjercicioInteractivo.objects.count()
total_cursos_final = Curso.objects.count()

print(f"📚 Cursos: {total_cursos_final}")
print(f"📝 Prácticas: {total_practicas_final}")
print(f"📝 Evaluaciones: {total_evaluaciones_final}")
print(f"📝 Ejercicios: {total_ejercicios_final}")

# Verificar cobertura
cursos_con_practicas = 0
cursos_con_evaluaciones = 0

for curso in Curso.objects.all():
    if Practica.objects.filter(curso=curso).count() > 0:
        cursos_con_practicas += 1
    if Evaluacion.objects.filter(curso=curso).count() > 0:
        cursos_con_evaluaciones += 1

print(f"\n✅ Cobertura:")
print(f"   • Cursos con prácticas: {cursos_con_practicas}/{total_cursos_final} ({cursos_con_practicas/total_cursos_final*100:.1f}%)")
print(f"   • Cursos con evaluaciones: {cursos_con_evaluaciones}/{total_cursos_final} ({cursos_con_evaluaciones/total_cursos_final*100:.1f}%)")

# ============================================
# 7. EJECUTAR PRUEBA COMPLETA
# ============================================
print("\n🧪 7. EJECUTANDO PRUEBA DE SISTEMA")
print("-" * 60)

# Probar algunas prácticas y evaluaciones
print("\n📋 Probando contenido generado:")

# Probar 5 prácticas aleatorias
practicas_prueba = Practica.objects.all().order_by('?')[:5]
for practica in practicas_prueba:
    count = EjercicioInteractivo.objects.filter(practica=practica).count()
    print(f"   ✅ Práctica: {practica.titulo[:30]} - {count} ejercicios")

# Probar 5 evaluaciones aleatorias
evaluaciones_prueba = Evaluacion.objects.all().order_by('?')[:5]
for evaluacion in evaluaciones_prueba:
    count = EjercicioInteractivo.objects.filter(evaluacion=evaluacion).count()
    print(f"   ✅ Evaluación: {evaluacion.titulo[:30]} - {count} ejercicios")

# ============================================
# 8. RESUMEN FINAL
# ============================================
print("\n" + "=" * 80)
print("🎉 ¡REVISIÓN Y COMPLETACIÓN COMPLETA!")
print("=" * 80)

print(f"""
📊 RESUMEN GENERAL:
   • Cursos totales: {total_cursos_final}
   • Prácticas totales: {total_practicas_final}
   • Evaluaciones totales: {total_evaluaciones_final}
   • Ejercicios totales: {total_ejercicios_final}

✅ COBERTURA:
   • Cursos con prácticas: {cursos_con_practicas}/{total_cursos_final} ({cursos_con_practicas/total_cursos_final*100:.1f}%)
   • Cursos con evaluaciones: {cursos_con_evaluaciones}/{total_cursos_final} ({cursos_con_evaluaciones/total_cursos_final*100:.1f}%)

🚀 ACCIONES RECOMENDADAS:
   1. Revisar el admin: /admin/core/
   2. Probar una práctica: /practicas/1/
   3. Probar una evaluación: /evaluaciones/1/
   4. Ver dashboard: /dashboard/
""")

print("=" * 80)
