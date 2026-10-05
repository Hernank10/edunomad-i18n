#!/usr/bin/env python3
"""
Script para importar todos los archivos de ejercicios a la base de datos
"""
import os
import re
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import RecursoEducativo

# Ruta de la carpeta con los ejercicios
RUTA_EJERCICIOS = 'apps/ejercicios_completos-lengua-castellana'

print("📚 IMPORTANDO RECURSOS EDUCATIVOS")
print("=" * 60)

if not os.path.exists(RUTA_EJERCICIOS):
    print(f"❌ La carpeta {RUTA_EJERCICIOS} no existe")
    exit()

# Obtener todos los archivos
archivos = []
for root, dirs, files in os.walk(RUTA_EJERCICIOS):
    for file in files:
        # Excluir archivos de sistema
        if file.startswith('.') or file in ['desktop.ini', 'Thumbs.db']:
            continue
        archivos.append(os.path.join(root, file))

print(f"📂 Encontrados {len(archivos)} archivos")

# Clasificar por extensión
extensiones = {}
for archivo in archivos:
    ext = os.path.splitext(archivo)[1].lower()
    extensiones[ext] = extensiones.get(ext, 0) + 1

print("\n📊 Distribución por extensión:")
for ext, count in sorted(extensiones.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {ext or 'sin extensión'}: {count} archivos")

# Función para extraer categoría del nombre
def extraer_categoria(nombre):
    nombre_lower = nombre.lower()
    categorias = {
        'sintaxis': ['sintaxis', 'sintáctica', 'morfosintaxis', 'oraciones'],
        'gramatica': ['gramática', 'gramatica', 'morfología', 'morfologia'],
        'redaccion': ['redacción', 'redaccion', 'escritura', 'redact'],
        'ortografia': ['ortografía', 'ortografia', 'puntuación', 'puntuacion'],
        'retorica': ['retórica', 'retorica', 'figuras', 'argumentativo'],
        'narrativa': ['narrativa', 'narrativo', 'cuento', 'historias'],
        'literatura': ['literatura', 'poesía', 'poesia', 'lírica'],
        'ciencia_ficcion': ['ciencia ficción', 'ciencia ficcion', 'sci-fi'],
        'conectores': ['conectores', 'conexiones'],
        'etimologia': ['etimología', 'etimologia', 'raíces', 'grecolatinas'],
        'linguistica': ['lingüística', 'linguistica', 'semántica', 'pragmática'],
        'fonetica': ['fonética', 'fonetica', 'fonología', 'fonologia'],
    }
    
    for cat, keywords in categorias.items():
        if any(kw in nombre_lower for kw in keywords):
            return cat
    return 'general'

print("\n🔄 Importando archivos...")
importados = 0
errores = 0

for archivo in archivos:
    try:
        nombre = os.path.basename(archivo)
        ruta = os.path.relpath(archivo, '.')
        extension = os.path.splitext(archivo)[1].lower()
        tamanio = os.path.getsize(archivo)
        categoria = extraer_categoria(nombre)
        
        # Crear el recurso
        recurso, created = RecursoEducativo.objects.get_or_create(
            ruta_completa=ruta,
            defaults={
                'nombre_archivo': nombre[:500],
                'extension': extension,
                'categoria': categoria,
                'tipo_contenido': 'Ejercicio' if extension in ['.html', '.htm'] else 'Dato',
                'tamanio_bytes': tamanio,
                'fecha_creacion': datetime.now(),
                'fecha_modificacion': datetime.now(),
                'descripcion': f"Recurso educativo: {nombre[:100]}",
                'etiquetas': categoria,
            }
        )
        
        if created:
            importados += 1
            if importados % 50 == 0:
                print(f"  Importados {importados} archivos...")
                
    except Exception as e:
        errores += 1
        if errores <= 5:
            print(f"❌ Error con {nombre}: {e}")

print(f"\n✅ {importados} recursos importados correctamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")

print(f"📊 Total recursos en BD: {RecursoEducativo.objects.count()}")

# Mostrar categorías
print("\n📂 Categorías creadas:")
categorias = RecursoEducativo.objects.values_list('categoria', flat=True).distinct()
for cat in sorted(categorias):
    count = RecursoEducativo.objects.filter(categoria=cat).count()
    print(f"  - {cat}: {count} recursos")
