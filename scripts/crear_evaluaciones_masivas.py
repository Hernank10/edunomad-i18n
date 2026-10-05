#!/usr/bin/env python3
"""
Script para generar evaluaciones masivas para todos los cursos y lecciones
"""
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso

# Verificar qué modelo de evaluación usar
try:
    from apps.core.models import Evaluacion, Pregunta
    from apps.core.models import Lesson
    print("✅ Usando modelo Evaluacion de core")
except ImportError:
    try:
        from apps.language_practice.models import Evaluation, Question
        print("✅ Usando modelo Evaluation de language_practice")
    except ImportError:
        print("❌ No se encontró modelo de evaluación. Creando en core...")
        # El modelo se creó arriba

# Intentar importar Lesson
try:
    from apps.language_practice.models import Lesson
    print("✅ Usando Lesson de language_practice")
except ImportError:
    from apps.core.models import Lesson
    print("✅ Usando Lesson de core")

print("📚 GENERANDO EVALUACIONES MASIVAS")
print("=" * 60)

# Obtener cursos
cursos = Curso.objects.all()
print(f"🎓 Cursos encontrados: {cursos.count()}")

if cursos.count() == 0:
    print("❌ No hay cursos. Primero crea cursos.")
    exit()

# Datos para generar preguntas
temas_generales = [
    "Conceptos básicos", "Fundamentos", "Teoría", "Práctica", 
    "Aplicación", "Análisis", "Síntesis", "Evaluación"
]

tipos_pregunta = ['OPCION_MULTIPLE', 'VERDADERO_FALSO', 'TEXTO', 'NUMERICA']

def generar_preguntas(tipo, tema, num_preguntas=5):
    """Genera preguntas según el tipo y tema"""
    preguntas = []
    
    for i in range(num_preguntas):
        tipo_preg = random.choice(tipos_pregunta)
        
        if tipo_preg == 'OPCION_MULTIPLE':
            pregunta = {
                'tipo': 'OPCION_MULTIPLE',
                'texto': f"¿Cuál es el concepto principal de {tema}? (Pregunta {i+1})",
                'opciones': [
                    f"Opción A - Concepto sobre {tema}",
                    f"Opción B - Concepto relacionado con {tema}",
                    f"Opción C - Concepto avanzado de {tema}",
                    f"Opción D - Concepto básico de {tema}"
                ],
                'respuesta_correcta': "Opción A - Concepto sobre {tema}",
                'puntaje': 5
            }
        elif tipo_preg == 'VERDADERO_FALSO':
            pregunta = {
                'tipo': 'VERDADERO_FALSO',
                'texto': f"¿Es correcto afirmar que {tema} es fundamental?",
                'opciones': ['Verdadero', 'Falso'],
                'respuesta_correcta': 'Verdadero',
                'puntaje': 3
            }
        elif tipo_preg == 'TEXTO':
            pregunta = {
                'tipo': 'TEXTO',
                'texto': f"Explica brevemente la importancia de {tema}:",
                'opciones': [],
                'respuesta_correcta': f"Respuesta sobre {tema}",
                'puntaje': 10
            }
        else:  # NUMERICA
            pregunta = {
                'tipo': 'NUMERICA',
                'texto': f"¿Cuántos conceptos principales tiene {tema}?",
                'opciones': [],
                'respuesta_correcta': str(random.randint(3, 8)),
                'puntaje': 5
            }
        
        preguntas.append(pregunta)
    
    return preguntas

print("\n🔄 Generando evaluaciones...")
evaluaciones_creadas = 0
errores = 0

for curso in cursos:
    # Obtener lecciones del curso
    try:
        lecciones = Lesson.objects.filter(course=curso) if hasattr(curso, 'course') else Lesson.objects.filter(curso=curso)
    except:
        lecciones = []
    
    if not lecciones:
        print(f"⚠️ {curso.titulo}: sin lecciones, creando 1 evaluación")
        num_evaluaciones = 1
    else:
        num_evaluaciones = min(random.randint(2, 4), len(lecciones))
    
    print(f"\n📖 Curso: {curso.titulo}")
    print(f"   Generando {num_evaluaciones} evaluaciones...")
    
    # Seleccionar lecciones aleatorias
    lecciones_seleccionadas = random.sample(list(lecciones), min(num_evaluaciones, len(lecciones))) if lecciones else []
    
    for i in range(num_evaluaciones):
        try:
            # Seleccionar tema
            tema = random.choice(temas_generales)
            
            # Generar título
            prefijos = ["Quiz", "Evaluación", "Examen", "Práctica", "Proyecto"]
            prefijo = random.choice(prefijos)
            titulo = f"{prefijo} de {tema} - {curso.titulo[:20]}"
            
            # Generar preguntas
            num_preguntas = random.randint(5, 10)
            preguntas = generar_preguntas('', tema, num_preguntas)
            
            # Crear evaluación
            evaluacion = Evaluacion.objects.create(
                curso=curso,
                titulo=titulo[:200],
                descripcion=f"Evaluación sobre {tema} para el curso {curso.titulo}",
                tipo=random.choice(['QUIZ', 'EXAMEN', 'PRACTICA', 'PROYECTO']),
                preguntas=preguntas,
                puntaje_maximo=sum(p['puntaje'] for p in preguntas),
                duracion_minutos=random.randint(15, 60),
                fecha_publicacion=datetime.now(),
                fecha_limite=datetime.now() + timedelta(days=random.randint(3, 14)),
                is_active=True,
            )
            
            # Asignar lecciones (si hay)
            if lecciones_seleccionadas and i < len(lecciones_seleccionadas):
                evaluacion.lecciones.add(lecciones_seleccionadas[i])
            
            evaluaciones_creadas += 1
            
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"   ❌ Error en evaluación {i+1}: {e}")

print("\n" + "=" * 60)
print(f"🎉 {evaluaciones_creadas} evaluaciones creadas exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")
print(f"📊 Total evaluaciones: {Evaluacion.objects.count()}")

# Mostrar resumen por curso
print("\n📋 RESUMEN POR CURSO:")
for curso in cursos:
    count = Evaluacion.objects.filter(curso=curso).count()
    if count > 0:
        print(f"  - {curso.titulo[:40]}: {count} evaluaciones")
