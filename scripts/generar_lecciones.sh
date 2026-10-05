#!/bin/bash

echo "🚀 GENERANDO LECCIONES MASIVAS"

# 1. Sincronizar cursos
python sincronizar_cursos.py

# 2. Crear lecciones
python crear_lecciones_corregido.py

# 3. Verificar
echo ""
echo "📊 VERIFICANDO:"
sqlite3 db.sqlite3 "SELECT 'Total lecciones: ' || COUNT(*) FROM language_practice_lesson;"

echo ""
echo "✅ ¡LECCIONES GENERADAS!"
echo "📝 Ejecuta: python manage.py runserver"
