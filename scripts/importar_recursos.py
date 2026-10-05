#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.utils import timezone
from apps.core.models import RecursoEducativo

if not os.path.exists('recursos_educativos.db'):
    print('⚠️  No se encontró recursos_educativos.db para importar.')
    exit(0)

conn = sqlite3.connect('recursos_educativos.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT nombre_archivo, ruta_completa, extension, categoria, 
           tipo_contenido, tamanio_bytes, fecha_creacion, 
           fecha_modificacion, descripcion
    FROM recursos
''')

datos = cursor.fetchall()
print(f'📂 Procesando {len(datos)} recursos hacia apps.core...')

def parse_fecha(fecha_str):
    if not fecha_str:
        return timezone.now()
    try:
        # Intenta parsear formato ISO estándar (YYYY-MM-DD HH:MM:SS)
        dt = datetime.fromisoformat(str(fecha_str).replace('Z', ''))
        if timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt
    except ValueError:
        return timezone.now()

importados = 0
for dato in datos:
    fecha_crea = parse_fecha(dato[6])
    fecha_mod = parse_fecha(dato[7])

    _, created = RecursoEducativo.objects.get_or_create(
        nombre_archivo=dato[0],
        defaults={
            'ruta_completa': dato[1] or '',
            'extension': dato[2] or '',
            'categoria': dato[3] or 'General',
            'tipo_contenido': dato[4] or '',
            'tamanio_bytes': dato[5] or 0,
            'fecha_creacion': fecha_crea,
            'fecha_modificacion': fecha_mod,
            'descripcion': dato[8] or ''
        }
    )
    if created:
        importados += 1

print(f'✅ Importados correctamente: {importados} nuevos recursos.')
print(f'📊 Total registrado en la Base de Datos: {RecursoEducativo.objects.count()}')
