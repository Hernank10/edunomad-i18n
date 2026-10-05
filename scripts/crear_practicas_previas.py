#!/usr/bin/env python3
"""
Script para generar prácticas previas (pre-tests) masivas para todas las lecciones
"""
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso

# Intentar importar modelos
try:
    from apps.core.models import PracticaPrevia, Lesson
    print("✅ Usando modelo PracticaPrevia de core")
except ImportError:
    print("❌ No se encontró modelo PracticaPrevia. Creando en core...")

# Intentar importar Lesson
try:
    from apps.language_practice.models import Lesson
    print("✅ Usando Lesson de language_practice")
except ImportError:
    from apps.core.models import Lesson
    print("✅ Usando Lesson de core")

print("📚 GENERANDO PRÁCTICAS PREVIAS MASIVAS")
print("=" * 60)

# Obtener cursos
cursos = Curso.objects.all()
print(f"🎓 Cursos encontrados: {cursos.count()}")

if cursos.count() == 0:
    print("❌ No hay cursos. Primero crea cursos.")
    exit()

# Datos para generar preguntas de diagnóstico
temas_diagnostico = [
    "Conocimientos previos", "Conceptos básicos", "Experiencia previa",
    "Familiaridad con el tema", "Habilidades iniciales", "Bases conceptuales"
]

tipos_pregunta = ['OPCION_MULTIPLE', 'VERDADERO_FALSO', 'TEXTO', 'NUMERICA']

def generar_preguntas_diagnostico(tema, num_preguntas=5):
    """Genera preguntas de diagnóstico para la práctica previa"""
    preguntas = []
    
    for i in range(num_preguntas):
        tipo_preg = random.choice(tipos_pregunta)
        
        if tipo_preg == 'OPCION_MULTIPLE':
            pregunta = {
                'tipo': 'OPCION_MULTIPLE',
                'texto': f"¿Qué conoces sobre {tema}? (Pregunta {i+1})",
                'opciones': [
                    f"Nada sobre {tema}",
                    f"Algo sobre {tema}",
                    f"Bastante sobre {tema}",
                    f"Mucho sobre {tema}"
                ],
                'respuesta_correcta': f"Algo sobre {tema}",
                'puntaje': 5,
                'es_diagnostico': True
            }
        elif tipo_preg == 'VERDADERO_FALSO':
            pregunta = {
                'tipo': 'VERDADERO_FALSO',
                'texto': f"¿Tienes experiencia previa con {tema}?",
                'opciones': ['Verdadero', 'Falso'],
                'respuesta_correcta': 'Verdadero',
                'puntaje': 3,
                'es_diagnostico': True
            }
        elif tipo_preg == 'TEXTO':
            pregunta = {
                'tipo': 'TEXTO',
                'texto': f"Describe brevemente tu experiencia con {tema}:",
                'opciones': [],
                'respuesta_correcta': f"Experiencia con {tema}",
                'puntaje': 10,
                'es_diagnostico': True
            }
        else:  # NUMERICA
            pregunta = {
                'tipo': 'NUMERICA',
                'texto': f"¿Cuánto te interesa aprender sobre {tema}? (1-10)",
                'opciones': [],
                'respuesta_correcta': '7',
                'puntaje': 5,
                'es_diagnostico': True
            }
        
        preguntas.append(pregunta)
    
    return preguntas

print("\n🔄 Generando prácticas previas...")
practicas_creadas = 0
errores = 0

for curso in cursos:
    # Obtener lecciones del curso
    try:
        lecciones = Lesson.objects.filter(course=curso) if hasattr(curso, 'course') else Lesson.objects.filter(curso=curso)
    except:
        lecciones = Lesson.objects.filter(curso=curso) if hasattr(curso, 'curso') else []
    
    if not lecciones:
        print(f"⚠️ {curso.titulo}: sin lecciones, omitiendo...")
        continue
    
    print(f"\n📖 Curso: {curso.titulo}")
    print(f"   Lecciones: {lecciones.count()}")
    
    # Generar práctica previa para cada lección (o cada 2-3 lecciones)
    lecciones_seleccionadas = list(lecciones)
    lecciones_a_procesar = random.sample(lecciones_seleccionadas, min(len(lecciones_seleccionadas), 10))
    
    for leccion in lecciones_a_procesar:
        try:
            # Decidir si crear práctica previa (80% de probabilidad)
            if random.random() > 0.8:
                continue
            
            # Seleccionar tema
            tema = random.choice(temas_diagnostico)
            
            # Generar título
            prefijos = ["Diagnóstico", "Pre-Test", "Evaluación Inicial", "Conocimientos Previos", "Preparación"]
            prefijo = random.choice(prefijos)
            titulo = f"{prefijo}: {leccion.title[:50]}"
            
            # Generar preguntas de diagnóstico
            num_preguntas = random.randint(3, 6)
            preguntas = generar_preguntas_diagnostico(tema, num_preguntas)
            
            # Crear práctica previa
            practica = PracticaPrevia.objects.create(
                leccion=leccion,
                titulo=titulo[:200],
                descripcion=f"Práctica previa para evaluar conocimientos sobre {tema} antes de la lección",
                tipo=random.choice(['DIAGNOSTICO', 'PRE_TEST', 'REPASO', 'PREPARACION']),
                preguntas=preguntas,
                puntaje_maximo=sum(p['puntaje'] for p in preguntas),
                duracion_minutos=random.randint(10, 25),
                es_obligatoria=random.choice([True, False]),
                is_active=True,
            )
            
            practicas_creadas += 1
            
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"   ❌ Error en práctica para lección {leccion.title[:30]}: {e}")
    
    print(f"   ✅ Prácticas creadas: {PracticaPrevia.objects.filter(leccion__in=lecciones).count()}")

print("\n" + "=" * 60)
print(f"🎉 {practicas_creadas} prácticas previas creadas exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")
print(f"📊 Total prácticas previas: {PracticaPrevia.objects.count()}")

# Mostrar resumen por curso
print("\n📋 RESUMEN POR CURSO:")
for curso in cursos:
    try:
        lecciones = Lesson.objects.filter(course=curso) if hasattr(curso, 'course') else Lesson.objects.filter(curso=curso)
        count = PracticaPrevia.objects.filter(leccion__in=lecciones).count()
        if count > 0:
            print(f"  - {curso.titulo[:40]}: {count} prácticas previas")
    except:
        pass
