#!/bin/bash

echo "🚀 GENERANDO PRÁCTICAS PREVIAS MASIVAS"

# 1. Verificar modelo de práctica previa
python manage.py shell -c "
from django.apps import apps
if apps.is_installed('language_practice'):
    print('✅ language_practice disponible')
else:
    print('⚠️ Usando modelos de core')
"

# 2. Ejecutar script de prácticas previas
python crear_practicas_previas.py

# 3. Verificar
echo ""
echo "📊 VERIFICANDO:"
sqlite3 db.sqlite3 "SELECT 'Total prácticas previas: ' || COUNT(*) FROM core_practicaprevia;"

echo ""
echo "✅ ¡PRÁCTICAS PREVIAS GENERADAS!"
echo "📝 Ejecuta: python manage.py runserver"
