#!/usr/bin/env python3
"""
Script para generar lecciones masivas para todos los cursos existentes
"""
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, RecursoEducativo

# Intentar importar Lesson si existe
try:
    from apps.language_practice.models import Lesson
    HAS_LESSON = True
except ImportError:
    HAS_LESSON = False
    print("⚠️ No se encontró el modelo Lesson. Se creará en apps.core.models")

# Si no existe Lesson, crearlo en core
if not HAS_LESSON:
    from django.db import models
    from apps.core.models import Curso
    
    class Lesson(models.Model):
        TIPOS = [
            ('VIDEO', 'Video'),
            ('TEXTO', 'Texto'),
            ('EJERCICIO', 'Ejercicio'),
            ('EVALUACION', 'Evaluación'),
            ('PDF', 'PDF'),
        ]
        
        curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='lecciones')
        titulo = models.CharField(max_length=200)
        descripcion = models.TextField(blank=True, null=True)
        tipo = models.CharField(max_length=20, choices=TIPOS, default='TEXTO')
        orden = models.IntegerField(default=0)
        contenido = models.TextField(blank=True, null=True)
        duracion_minutos = models.IntegerField(default=15)
        recursos = models.ManyToManyField(RecursoEducativo, blank=True)
        is_published = models.BooleanField(default=True)
        fecha_creacion = models.DateTimeField(auto_now_add=True)
        fecha_actualizacion = models.DateTimeField(auto_now=True)
        
        class Meta:
            ordering = ['orden', 'fecha_creacion']
            unique_together = ['curso', 'orden']
        
        def __str__(self):
            return f"{self.curso.titulo[:30]} - Lección {self.orden}: {self.titulo[:30]}"
    
    print("✅ Modelo Lesson creado en apps.core.models")
    
    # Importar el modelo para usarlo
    from apps.core.models import Lesson

print("📚 GENERANDO LECCIONES MASIVAS")
print("=" * 60)

# Obtener todos los cursos
cursos = Curso.objects.all()
print(f"🎓 Cursos encontrados: {cursos.count()}")

if cursos.count() == 0:
    print("❌ No hay cursos. Primero crea cursos.")
    exit()

# Datos para generar lecciones
tipos_leccion = ['VIDEO', 'TEXTO', 'EJERCICIO', 'EVALUACION', 'PDF']
prefijos_titulos = [
    "Introducción a", "Fundamentos de", "Conceptos básicos de",
    "Profundizando en", "Avanzando con", "Aplicación práctica de",
    "Ejercicios sobre", "Evaluación de", "Taller de", "Proyecto sobre"
]

sufijos_titulos = [
    "Conceptos Clave", "Primeros Pasos", "Ejemplos Prácticos",
    "Casos de Estudio", "Ejercicios Resueltos", "Proyecto Guiado",
    "Evaluación Final", "Recursos Adicionales", "Síntesis", "Aplicación"
]

contenidos = [
    "En esta lección aprenderás los conceptos fundamentales.",
    "Exploraremos en detalle los temas principales con ejemplos.",
    "Esta lección incluye ejercicios prácticos para reforzar el aprendizaje.",
    "Aquí pondremos en práctica lo aprendido con casos reales.",
    "Evaluaremos tu comprensión con preguntas y ejercicios.",
    "Profundizaremos en los aspectos más complejos del tema.",
    "Aplicaremos los conceptos en situaciones reales.",
    "Revisaremos y sintetizaremos los puntos clave.",
]

# Función para generar contenido específico por tipo
def generar_contenido(tipo, tema):
    contenidos_por_tipo = {
        'VIDEO': f"""
<h3>🎥 Video: {tema}</h3>
<p>En este video aprenderás sobre {tema} de manera visual y práctica.</p>
<ul>
    <li>Introducción al tema</li>
    <li>Explicación detallada con ejemplos</li>
    <li>Demostración práctica</li>
    <li>Resumen y conclusiones</li>
</ul>
<p><strong>Duración recomendada:</strong> 15-20 minutos</p>
""",
        'TEXTO': f"""
<h3>📖 Texto: {tema}</h3>
<p>Contenido teórico sobre {tema}.</p>
<h4>1. Introducción</h4>
<p>Los fundamentos de {tema} son esenciales para...</p>
<h4>2. Conceptos Clave</h4>
<ul>
    <li>Concepto 1: Definición y aplicación</li>
    <li>Concepto 2: Ejemplos prácticos</li>
    <li>Concepto 3: Casos de uso</li>
</ul>
<h4>3. Resumen</h4>
<p>En resumen, los puntos más importantes de {tema} son...</p>
""",
        'EJERCICIO': f"""
<h3>✏️ Ejercicios: {tema}</h3>
<p>Resuelve los siguientes ejercicios sobre {tema}:</p>
<ol>
    <li><strong>Ejercicio 1:</strong> Describe brevemente...</li>
    <li><strong>Ejercicio 2:</strong> Resuelve el siguiente problema...</li>
    <li><strong>Ejercicio 3:</strong> Analiza el caso y propón...</li>
    <li><strong>Ejercicio 4:</strong> Reflexiona sobre...</li>
</ol>
<p><strong>Instrucciones:</strong> Responde cada pregunta en el espacio indicado.</p>
""",
        'EVALUACION': f"""
<h3>📝 Evaluación: {tema}</h3>
<p>Responde las siguientes preguntas sobre {tema}:</p>
<ol>
    <li><strong>Pregunta 1:</strong> ¿Cuál es la definición de...?</li>
    <li><strong>Pregunta 2:</strong> Explica el concepto de...</li>
    <li><strong>Pregunta 3:</strong> ¿Cuáles son las características de...?</li>
    <li><strong>Pregunta 4:</strong> Aplica los conocimientos en...</li>
    <li><strong>Pregunta 5:</strong> Reflexiona sobre la importancia de...</li>
</ol>
<p><strong>Puntuación:</strong> 20 puntos por pregunta.</p>
""",
        'PDF': f"""
<h3>📄 Material PDF: {tema}</h3>
<p>Documento descargable sobre {tema}.</p>
<p><strong>Contenido del PDF:</strong></p>
<ul>
    <li>Portada e introducción</li>
    <li>Desarrollo del tema (5-7 páginas)</li>
    <li>Ejercicios y actividades</li>
    <li>Bibliografía y recursos adicionales</li>
</ul>
<p><strong>Descargar:</strong> <a href="#">Haz clic aquí para descargar el PDF</a></p>
"""
    }
    return contenidos_por_tipo.get(tipo, contenidos[0])

print("\n🔄 Generando lecciones...")
lecciones_creadas = 0
errores = 0

for curso in cursos:
    # Número aleatorio de lecciones por curso (5-12)
    num_lecciones = random.randint(5, 12)
    print(f"\n📖 Curso: {curso.titulo}")
    print(f"   Generando {num_lecciones} lecciones...")
    
    # Obtener recursos del curso
    recursos_curso = list(curso.recursos.all())
    
    for i in range(num_lecciones):
        try:
            # Seleccionar tipo
            tipo = random.choice(tipos_leccion)
            
            # Generar título
            prefijo = random.choice(prefijos_titulos)
            sufijo = random.choice(sufijos_titulos)
            titulo = f"{prefijo} {curso.categoria} - {sufijo}"
            
            # Generar descripción
            descripcion = f"Lección {i+1} sobre {curso.categoria}: {titulo}"
            
            # Generar contenido
            contenido = generar_contenido(tipo, curso.categoria)
            
            # Crear lección
            leccion = Lesson.objects.create(
                curso=curso,
                titulo=titulo[:200],
                descripcion=descripcion,
                tipo=tipo,
                orden=i + 1,
                contenido=contenido,
                duracion_minutos=random.randint(10, 45),
                is_published=True,
            )
            
            # Asignar recursos relacionados (si hay)
            if recursos_curso:
                num_recursos = min(random.randint(1, 3), len(recursos_curso))
                recursos_seleccionados = random.sample(recursos_curso, num_recursos)
                leccion.recursos.add(*recursos_seleccionados)
            
            lecciones_creadas += 1
            
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"   ❌ Error al crear lección {i+1}: {e}")
    
    print(f"   ✅ Lecciones creadas: {num_lecciones}")

print("\n" + "=" * 60)
print(f"🎉 {lecciones_creadas} lecciones creadas exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")
print(f"📊 Total lecciones: {Lesson.objects.count()}")

# Mostrar resumen por curso
print("\n📋 RESUMEN POR CURSO:")
for curso in cursos:
    count = Lesson.objects.filter(curso=curso).count()
    print(f"  - {curso.titulo[:40]}: {count} lecciones")
