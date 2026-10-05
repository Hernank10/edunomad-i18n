#!/usr/bin/env python3
"""
Programa para generar 100 nuevos cursos basados en técnicas de redacción
Utiliza los recursos de la carpeta ejercicios_completos-lengua-castellana
"""
import os
import re
import random
from datetime import datetime
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, RecursoEducativo
from django.db import models

print("=" * 80)
print("📚 GENERANDO 100 NUEVOS CURSOS")
print("=" * 80)

# ============================================
# 1. ANALIZAR CURSOS EXISTENTES
# ============================================
print("\n📊 1. ANALIZANDO CURSOS EXISTENTES")
print("-" * 60)

cursos_existentes = Curso.objects.all()
print(f"✅ Cursos existentes: {cursos_existentes.count()}")

# Categorías existentes
categorias_existentes = cursos_existentes.values_list('categoria', flat=True).distinct()
print(f"📂 Categorías existentes: {list(categorias_existentes)}")

# Recursos disponibles
total_recursos = RecursoEducativo.objects.count()
print(f"📚 Recursos disponibles: {total_recursos}")

# ============================================
# 2. EXTRAER TÉCNICAS DE REDACCIÓN DE RECURSOS
# ============================================
print("\n📝 2. EXTRAYENDO TÉCNICAS DE REDACCIÓN")
print("-" * 60)

# Obtener todos los recursos de redacción
recursos_redaccion = RecursoEducativo.objects.filter(
    categoria__in=['redaccion', 'sintaxis', 'gramatica', 'ortografia', 'retorica', 'narrativa']
)

print(f"✅ Recursos de redacción: {recursos_redaccion.count()}")

# Extraer técnicas de los nombres de archivo
tecnicas = []
for recurso in recursos_redaccion:
    nombre = recurso.nombre_archivo
    # Limpiar nombre
    nombre = re.sub(r'\.(html|json|md|txt)$', '', nombre)
    nombre = re.sub(r'^\d+\s*', '', nombre)
    nombre = nombre.replace('_', ' ').strip()
    
    # Extraer técnicas
    if 'técnica' in nombre.lower() or 'tecnica' in nombre.lower():
        tecnicas.append(nombre)
    elif 'técnicas' in nombre.lower() or 'tecnicas' in nombre.lower():
        tecnicas.append(nombre)

print(f"✅ Técnicas extraídas: {len(tecnicas)}")

# Mostrar algunas técnicas
print(f"\n📋 Ejemplos de técnicas:")
for t in tecnicas[:10]:
    print(f"   - {t[:80]}")

# ============================================
# 3. CATEGORÍAS Y TEMAS PARA NUEVOS CURSOS
# ============================================
print("\n📂 3. CATEGORÍAS Y TEMAS PARA NUEVOS CURSOS")
print("-" * 60)

# Categorías de redacción
categorias_redaccion = [
    'Redacción Científica',
    'Redacción Académica',
    'Redacción Periodística',
    'Redacción Literaria',
    'Redacción Técnica',
    'Redacción Creativa',
    'Redacción Corporativa',
    'Redacción Digital',
    'Redacción Publicitaria',
    'Redacción Jurídica',
]

# Niveles educativos
niveles = ['PRIMARIA', 'SECUNDARIA', 'BACHILLERATO', 'UNIVERSITARIO', 'POSGRADO']

# Estados
estados = ['BORRADOR', 'PUBLICADO']

# Precios
precios = [0, 9.99, 19.99, 29.99, 39.99, 49.99, 59.99, 79.99, 99.99]

# ============================================
# 4. GENERAR CURSOS
# ============================================
print("\n🔄 4. GENERANDO 100 NUEVOS CURSOS")
print("-" * 60)

cursos_creados = 0
errores = 0

# Distribuir cursos por categoría
cursos_por_categoria = {}
for categoria in categorias_redaccion:
    # Cada categoría tendrá entre 5 y 15 cursos
    num_cursos = random.randint(5, 15)
    cursos_por_categoria[categoria] = num_cursos

# Ajustar para llegar a 100
total_asignado = sum(cursos_por_categoria.values())
while total_asignado < 100:
    for categoria in categorias_redaccion:
        if total_asignado < 100:
            cursos_por_categoria[categoria] += 1
            total_asignado += 1

print(f"📋 Distribución de cursos:")
for cat, num in cursos_por_categoria.items():
    print(f"   - {cat}: {num} cursos")

# Función para generar descripción
def generar_descripcion(categoria, nivel):
    descripciones = [
        f"Curso completo de {categoria} para {nivel}. Aprende las técnicas más avanzadas.",
        f"Domina la {categoria} con este curso práctico y teórico. Nivel {nivel}.",
        f"Especialízate en {categoria} con ejercicios y ejemplos reales. Para {nivel}.",
        f"Curso intensivo de {categoria} con más de 100 técnicas. Perfecto para {nivel}.",
        f"Aprende {categoria} desde cero con metodología práctica. Nivel {nivel}.",
    ]
    return random.choice(descripciones)

# Función para generar palabras clave
def generar_palabras_clave(categoria):
    palabras = {
        'Redacción Científica': ['investigación', 'artículo', 'tesis', 'publicación', 'ciencia'],
        'Redacción Académica': ['ensayo', 'trabajo', 'universidad', 'investigación', 'tesis'],
        'Redacción Periodística': ['noticia', 'reportaje', 'entrevista', 'crónica', 'periodismo'],
        'Redacción Literaria': ['novela', 'cuento', 'poesía', 'narrativa', 'literatura'],
        'Redacción Técnica': ['manual', 'documentación', 'especificaciones', 'técnica', 'informe'],
        'Redacción Creativa': ['creatividad', 'escritura', 'inspiración', 'imaginación', 'arte'],
        'Redacción Corporativa': ['empresa', 'corporativo', 'informe', 'presentación', 'negocios'],
        'Redacción Digital': ['web', 'blog', 'redes sociales', 'contenido', 'digital'],
        'Redacción Publicitaria': ['publicidad', 'marketing', 'persuasión', 'ventas', 'campaña'],
        'Redacción Jurídica': ['legal', 'contrato', 'demanda', 'jurídico', 'abogacía'],
    }
    return palabras.get(categoria, ['redacción', 'escritura', 'técnicas'])

# Función para asignar recursos
def asignar_recursos(curso, categoria):
    # Buscar recursos relacionados
    recursos_relacionados = RecursoEducativo.objects.filter(
        categoria__icontains=categoria.split()[0].lower()
    )
    
    if not recursos_relacionados.exists():
        # Buscar recursos generales de redacción
        recursos_relacionados = RecursoEducativo.objects.filter(
            categoria__in=['redaccion', 'sintaxis', 'gramatica']
        )
    
    # Seleccionar entre 3 y 8 recursos
    num_recursos = min(random.randint(3, 8), recursos_relacionados.count())
    if num_recursos > 0:
        recursos_seleccionados = random.sample(list(recursos_relacionados), num_recursos)
        curso.recursos.add(*recursos_seleccionados)
    return num_recursos

# Crear cursos
print("\n🔄 Creando cursos...")

for categoria, num_cursos in cursos_por_categoria.items():
    for i in range(num_cursos):
        try:
            nivel = random.choice(niveles)
            estado = random.choice(estados)
            precio = random.choice(precios)
            
            # Generar título
            prefijos = [
                f"Introducción a la {categoria}",
                f"{categoria} - Nivel {i+1}",
                f"Técnicas Avanzadas de {categoria}",
                f"Dominando la {categoria}",
                f"Curso de {categoria} para {nivel}"
            ]
            titulo = random.choice(prefijos)
            
            # Asegurar título único
            original_titulo = titulo
            contador = 1
            while Curso.objects.filter(titulo=titulo).exists():
                titulo = f"{original_titulo} ({contador})"
                contador += 1
            
            # Generar descripción
            descripcion = generar_descripcion(categoria, nivel)
            
            # Generar palabras clave
            palabras_clave = generar_palabras_clave(categoria)
            
            # Crear curso
            curso = Curso.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                categoria=categoria,
                nivel=nivel,
                estado=estado,
                duracion_horas=random.randint(8, 40),
                palabras_clave=', '.join(random.sample(palabras_clave, min(3, len(palabras_clave)))),
                precio=precio,
                imagen_url=f"https://via.placeholder.com/800x400?text={categoria.replace(' ', '+')}+Curso"
            )
            
            # Asignar recursos
            num_recursos = asignar_recursos(curso, categoria)
            
            cursos_creados += 1
            if cursos_creados % 10 == 0:
                print(f"  ✅ Generados {cursos_creados} cursos...")
                
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"❌ Error en curso {i+1} de {categoria}: {e}")

print(f"\n✅ {cursos_creados} cursos creados exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")

# ============================================
# 5. ESTADÍSTICAS FINALES
# ============================================
print("\n📊 5. ESTADÍSTICAS FINALES")
print("-" * 60)

total_cursos = Curso.objects.count()
print(f"📚 Total cursos en BD: {total_cursos}")

# Cursos por categoría
cursos_por_categoria = Curso.objects.values('categoria').annotate(
    count=models.Count('id')
).order_by('-count')

print(f"\n📂 Cursos por categoría:")
for cat in cursos_por_categoria:
    print(f"   - {cat['categoria']}: {cat['count']} cursos")

# Cursos por nivel
cursos_por_nivel = Curso.objects.values('nivel').annotate(
    count=models.Count('id')
).order_by('-count')

print(f"\n📚 Cursos por nivel:")
for nivel in cursos_por_nivel:
    print(f"   - {nivel['nivel']}: {nivel['count']} cursos")

# Cursos por estado
cursos_por_estado = Curso.objects.values('estado').annotate(
    count=models.Count('id')
).order_by('-count')

print(f"\n📊 Cursos por estado:")
for estado in cursos_por_estado:
    print(f"   - {estado['estado']}: {estado['count']} cursos")

# Recursos utilizados
recursos_usados = set()
for curso in Curso.objects.all():
    for recurso in curso.recursos.all():
        recursos_usados.add(recurso.id)

print(f"\n📚 Recursos utilizados en cursos: {len(recursos_usados)}/{RecursoEducativo.objects.count()}")

# ============================================
# 6. VERIFICAR ALGUNOS CURSOS NUEVOS
# ============================================
print("\n🔍 6. VERIFICANDO CURSOS NUEVOS")
print("-" * 60)

cursos_nuevos = Curso.objects.all().order_by('-id')[:10]
print(f"\n📋 Últimos 10 cursos creados:")
for curso in cursos_nuevos:
    num_recursos = curso.recursos.count()
    print(f"   • {curso.titulo[:50]}")
    print(f"     Categoría: {curso.categoria}, Nivel: {curso.nivel}, Recursos: {num_recursos}")

# ============================================
# 7. RESUMEN
# ============================================
print("\n" + "=" * 80)
print("🎉 ¡GENERACIÓN DE 100 CURSOS COMPLETADA!")
print("=" * 80)

print(f"""
📊 RESUMEN FINAL:
   • Cursos creados: {cursos_creados}
   • Total cursos en BD: {total_cursos}
   • Categorías utilizadas: {len(cursos_por_categoria)}
   • Recursos utilizados: {len(recursos_usados)}
   • Errores: {errores}

📂 NUEVAS CATEGORÍAS CREADAS:
""")
for cat in cursos_por_categoria:
    if cat['categoria'] in categorias_redaccion:
        print(f"   ✅ {cat['categoria']}: {cat['count']} cursos")

print(f"""
🚀 ACCIONES RECOMENDADAS:
   1. Revisar los nuevos cursos en el admin: /admin/core/curso/
   2. Verificar la asignación de recursos
   3. Ajustar precios y duraciones según sea necesario
   4. Publicar los cursos en borrador

💡 PRÓXIMOS PASOS:
   1. Generar prácticas para los nuevos cursos
   2. Crear evaluaciones
   3. Asignar profesores a los cursos
   4. Inscribir estudiantes
""")

print("=" * 80)
