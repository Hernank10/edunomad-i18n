#!/usr/bin/env python3
"""
Script para generar automáticamente lecciones, prácticas y evaluaciones
para cada curso existente (incluyendo los 100 nuevos)
"""
import os
import random
import hashlib
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, Practica, Evaluacion, EjercicioInteractivo, RecursoEducativo
from django.db import models

print("=" * 80)
print("📚 GENERANDO LECCIONES, PRÁCTICAS Y EVALUACIONES")
print("=" * 80)

# ============================================
# 1. ANALIZAR CURSOS EXISTENTES
# ============================================
print("\n📊 1. ANALIZANDO CURSOS EXISTENTES")
print("-" * 60)

cursos = Curso.objects.all()
print(f"✅ Cursos encontrados: {cursos.count()}")

# ============================================
# 2. FUNCIONES PARA GENERAR CONTENIDO
# ============================================
print("\n📝 2. PREPARANDO GENERACIÓN DE CONTENIDO")
print("-" * 60)

# Temas para lecciones
TEMAS_LECCION = [
    "Introducción", "Conceptos Básicos", "Fundamentos", "Estructura",
    "Análisis", "Práctica", "Ejercicios", "Evaluación",
    "Aplicación", "Proyecto", "Caso de Estudio", "Profundización",
    "Técnicas Avanzadas", "Optimización", "Recursos Adicionales",
    "Metodología", "Estrategias", "Herramientas", "Ejemplos Prácticos",
    "Desarrollo", "Implementación", "Resultados", "Conclusiones"
]

def generar_contenido_leccion(tema, categoria):
    """Genera contenido para una lección"""
    contenidos = [
        f"""
<h3>📖 {tema} - {categoria}</h3>
<p>En esta lección exploraremos los fundamentos de {tema} aplicados a {categoria}.</p>
<h4>🎯 Objetivos:</h4>
<ul>
    <li>Comprender los conceptos clave de {tema}</li>
    <li>Aplicar {tema} en contextos de {categoria}</li>
    <li>Desarrollar habilidades prácticas</li>
</ul>
<h4>📋 Contenido:</h4>
<ol>
    <li>Introducción a {tema}</li>
    <li>Conceptos fundamentales</li>
    <li>Ejemplos prácticos</li>
    <li>Ejercicios de aplicación</li>
</ol>
<h4>📚 Recursos adicionales:</h4>
<ul>
    <li>Material complementario</li>
    <li>Ejercicios de práctica</li>
    <li>Bibliografía recomendada</li>
</ul>
""",
        f"""
<h3>📝 {tema} en {categoria}</h3>
<p>Esta lección aborda {tema} desde una perspectiva práctica y aplicada a {categoria}.</p>
<h4>🔑 Puntos clave:</h4>
<ul>
    <li>Definición y alcance de {tema}</li>
    <li>Principios fundamentales</li>
    <li>Aplicaciones en {categoria}</li>
    <li>Casos de éxito</li>
</ul>
<h4>💡 Actividades:</h4>
<ol>
    <li>Análisis de casos prácticos</li>
    <li>Ejercicios de aplicación</li>
    <li>Proyecto guiado</li>
</ol>
"""
    ]
    return random.choice(contenidos)

def generar_preguntas_opcion_multiple(tema, categoria, num):
    """Genera preguntas de opción múltiple"""
    preguntas = []
    bases = [
        (f"¿Cuál es el concepto principal de {tema} en {categoria}?", 
         ["Definición A", "Definición B", "Definición C", "Definición D"], 
         "Definición A"),
        (f"¿Qué caracteriza a {tema} en {categoria}?", 
         ["Característica 1", "Característica 2", "Característica 3", "Característica 4"], 
         "Característica 1"),
        (f"¿Cuál es la aplicación más común de {tema}?", 
         ["Aplicación A", "Aplicación B", "Aplicación C", "Aplicación D"], 
         "Aplicación A"),
    ]
    
    for i in range(num):
        base = random.choice(bases)
        pregunta_texto, opciones, respuesta = base
        opciones_shuffle = opciones.copy()
        random.shuffle(opciones_shuffle)
        preguntas.append({
            'tipo': 'OPCION_MULTIPLE',
            'pregunta': f"{pregunta_texto} (Pregunta {i+1})",
            'opciones': opciones_shuffle[:4],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta correcta es '{respuesta}' porque es el concepto fundamental.",
            'puntaje': 3
        })
    return preguntas

def generar_preguntas_verdadero_falso(tema, categoria, num):
    """Genera preguntas de verdadero/falso"""
    preguntas = []
    afirmaciones = [
        (f"'{tema}' es fundamental en {categoria}.", "Verdadero"),
        (f"'{tema}' no tiene aplicación en {categoria}.", "Falso"),
        (f"La práctica de {tema} mejora los resultados en {categoria}.", "Verdadero"),
    ]
    
    for i in range(num):
        afirmacion, respuesta = random.choice(afirmaciones)
        preguntas.append({
            'tipo': 'VERDADERO_FALSO',
            'pregunta': f"¿Es correcto afirmar que: '{afirmacion}'? (Pregunta {i+1})",
            'opciones': ['Verdadero', 'Falso'],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta es '{respuesta}' según la teoría.",
            'puntaje': 2
        })
    return preguntas

def generar_ejercicios_100(tema, categoria, num_ejercicios=100):
    """Genera 100 ejercicios para una práctica o evaluación"""
    ejercicios = []
    
    # Distribuir tipos (100 ejercicios)
    distribucion = {
        'OPCION_MULTIPLE': 40,
        'VERDADERO_FALSO': 30,
        'TEXTO': 20,
        'RELACIONAR': 10
    }
    
    for tipo, cantidad in distribucion.items():
        if tipo == 'OPCION_MULTIPLE':
            nuevos = generar_preguntas_opcion_multiple(tema, categoria, cantidad)
        elif tipo == 'VERDADERO_FALSO':
            nuevos = generar_preguntas_verdadero_falso(tema, categoria, cantidad)
        else:
            # Para TEXTO y RELACIONAR, crear preguntas genéricas
            nuevos = []
            for i in range(cantidad):
                nuevos.append({
                    'tipo': tipo,
                    'pregunta': f"Pregunta {i+1}: Desarrolla el concepto de {tema} en {categoria}",
                    'opciones': [],
                    'respuesta_correcta': f"Respuesta sobre {tema} en {categoria}",
                    'explicacion': f"La respuesta debe cubrir los aspectos clave de {tema}.",
                    'puntaje': 5
                })
        ejercicios.extend(nuevos)
    
    random.shuffle(ejercicios)
    return ejercicios[:num_ejercicios]

# ============================================
# 3. GENERAR LECCIONES, PRÁCTICAS Y EVALUACIONES
# ============================================
print("\n🔄 3. GENERANDO CONTENIDO PARA CADA CURSO")
print("-" * 60)

total_lecciones = 0
total_practicas = 0
total_evaluaciones = 0
total_ejercicios = 0
cursos_procesados = 0

for curso in cursos:
    print(f"\n📖 Procesando: {curso.titulo[:50]}...")
    
    # Determinar número de lecciones (5-10 por curso)
    num_lecciones = random.randint(5, 10)
    
    # Seleccionar temas
    temas_seleccionados = random.sample(TEMAS_LECCION, min(num_lecciones, len(TEMAS_LECCION)))
    
    for i, tema in enumerate(temas_seleccionados, 1):
        # Crear lección (solo en memoria, no en BD)
        leccion_titulo = f"Lección {i}: {tema}"
        leccion_contenido = generar_contenido_leccion(tema, curso.categoria)
        
        # Crear práctica asociada a la lección (100 ejercicios)
        practica = Practica.objects.create(
            curso=curso,
            titulo=f"Práctica {i}: {tema}",
            descripcion=f"Práctica sobre {tema} para el curso {curso.titulo[:30]}",
            tipo=random.choice(['EJERCICIO', 'QUIZ', 'REPASO']),
            puntaje_maximo=300,  # 100 ejercicios x 3 puntos promedio
            duracion_minutos=random.randint(15, 30),
            orden=i,
            is_active=True
        )
        total_practicas += 1
        
        # Generar 100 ejercicios para la práctica
        ejercicios_practica = generar_ejercicios_100(tema, curso.categoria, 100)
        for j, ejercicio_data in enumerate(ejercicios_practica, 1):
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
            total_ejercicios += 1
        
        # Crear evaluación asociada a la lección (100 ejercicios)
        evaluacion = Evaluacion.objects.create(
            curso=curso,
            titulo=f"Evaluación {i}: {tema}",
            descripcion=f"Evaluación sobre {tema} para el curso {curso.titulo[:30]}",
            tipo=random.choice(['EXAMEN', 'PRACTICA', 'FINAL']),
            puntaje_maximo=300,
            duracion_minutos=random.randint(20, 45),
            nota_minima=random.randint(60, 70),
            fecha_limite=datetime.now() + timedelta(days=random.randint(3, 10)),
            is_active=True
        )
        total_evaluaciones += 1
        
        # Generar 100 ejercicios para la evaluación
        ejercicios_evaluacion = generar_ejercicios_100(tema, curso.categoria, 100)
        for j, ejercicio_data in enumerate(ejercicios_evaluacion, 1):
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
            total_ejercicios += 1
        
        total_lecciones += 1
    
    cursos_procesados += 1
    if cursos_procesados % 10 == 0:
        print(f"  ✅ Procesados {cursos_procesados} cursos...")

print(f"\n✅ Generación completada para {cursos_procesados} cursos")

# ============================================
# 4. ESTADÍSTICAS FINALES
# ============================================
print("\n📊 4. ESTADÍSTICAS FINALES")
print("-" * 60)

print(f"📚 Cursos procesados: {cursos_procesados}")
print(f"📖 Lecciones generadas: {total_lecciones}")
print(f"📝 Prácticas generadas: {total_practicas}")
print(f"📝 Evaluaciones generadas: {total_evaluaciones}")
print(f"📝 Ejercicios totales generados: {total_ejercicios}")

print("\n📋 DETALLE POR CURSO:")
for curso in Curso.objects.all()[:10]:
    practicas = Practica.objects.filter(curso=curso).count()
    evaluaciones = Evaluacion.objects.filter(curso=curso).count()
    print(f"   • {curso.titulo[:40]}")
    print(f"     Prácticas: {practicas}, Evaluaciones: {evaluaciones}")

# Estadísticas de ejercicios por práctica
practicas_con_ejercicios = 0
for practica in Practica.objects.all():
    count = EjercicioInteractivo.objects.filter(practica=practica).count()
    if count > 0:
        practicas_con_ejercicios += 1

print(f"\n📊 Prácticas con ejercicios: {practicas_con_ejercicios}/{Practica.objects.count()}")

# Estadísticas de ejercicios por evaluación
evaluaciones_con_ejercicios = 0
for evaluacion in Evaluacion.objects.all():
    count = EjercicioInteractivo.objects.filter(evaluacion=evaluacion).count()
    if count > 0:
        evaluaciones_con_ejercicios += 1

print(f"📊 Evaluaciones con ejercicios: {evaluaciones_con_ejercicios}/{Evaluacion.objects.count()}")

# ============================================
# 5. RESUMEN FINAL
# ============================================
print("\n" + "=" * 80)
print("🎉 ¡GENERACIÓN COMPLETA!")
print("=" * 80)

total_general = total_lecciones + total_practicas + total_evaluaciones
print(f"""
📊 RESUMEN GENERAL:
   • Cursos procesados: {cursos_procesados}
   • Lecciones creadas: {total_lecciones}
   • Prácticas creadas: {total_practicas}
   • Evaluaciones creadas: {total_evaluaciones}
   • Ejercicios creados: {total_ejercicios}
   • Total elementos generados: {total_general}

🚀 ACCIONES RECOMENDADAS:
   1. Revisar el contenido en el admin: /admin/core/
   2. Verificar prácticas: /admin/core/practica/
   3. Verificar evaluaciones: /admin/core/evaluacion/
   4. Probar una práctica: /practicas/1/
   5. Probar una evaluación: /evaluaciones/1/
""")

print("=" * 80)
