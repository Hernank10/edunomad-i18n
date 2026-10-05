#!/bin/bash

echo "🚀 GENERANDO EVALUACIONES MASIVAS"

# 1. Verificar modelo de evaluación
python manage.py shell -c "
from django.apps import apps
if apps.is_installed('language_practice'):
    print('✅ language_practice disponible')
else:
    print('⚠️ Usando modelos de core')
"

# 2. Ejecutar script de evaluaciones
python crear_evaluaciones_masivas.py

# 3. Verificar
echo ""
echo "📊 VERIFICANDO:"
sqlite3 db.sqlite3 "SELECT 'Total evaluaciones: ' || COUNT(*) FROM core_evaluacion;"

echo ""
echo "✅ ¡EVALUACIONES GENERADAS!"
echo "📝 Ejecuta: python manage.py runserver"
