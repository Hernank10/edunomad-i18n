#!/bin/bash

echo "📜 GENERANDO CERTIFICADOS Y LOGROS"

# 1. Verificar modelo de certificado
python manage.py shell -c "
from django.apps import apps
if apps.is_installed('core'):
    print('✅ Core disponible')
else:
    print('⚠️ Verificando modelos...')
"

# 2. Ejecutar script de certificados
python crear_certificados_masivos.py

# 3. Verificar
echo ""
echo "📊 VERIFICANDO:"
sqlite3 db.sqlite3 "SELECT 'Total certificados: ' || COUNT(*) FROM core_certificado;"
sqlite3 db.sqlite3 "SELECT 'Total logros otorgados: ' || COUNT(*) FROM core_logrousuario;"

echo ""
echo "✅ ¡CERTIFICADOS Y LOGROS GENERADOS!"
echo "📝 Ejecuta: python manage.py runserver"
