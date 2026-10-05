# EduNomad

## Plataforma educativa para el aprendizaje de la escritura morfosintáctica del castellano

**EduNomad** es una plataforma educativa digital desarrollada en **Django**, orientada al aprendizaje progresivo, ético y pedagógicamente fundamentado de la **escritura morfosintáctica del español** como lengua meta. Está diseñada para estudiantes cuya lengua materna pertenece a las **diez lenguas más habladas del mundo**, así como para docentes, investigadores y autodidactas.

El proyecto integra principios de **lingüística aplicada**, **pedagogía contrastiva**, **tecnología educativa** y **desarrollo de software académico**, con una proyección futura hacia la integración responsable de **inteligencia artificial educativa**.

---

## 🎯 Objetivos del proyecto

### Objetivo general

Desarrollar una plataforma digital que facilite el aprendizaje consciente y progresivo de la escritura en lengua castellana, con énfasis en la morfosintaxis, respetando la diversidad lingüística y cultural de los estudiantes.

### Objetivos específicos

* Ofrecer cursos estructurados por niveles (A1–C2) centrados en la escritura.
* Proporcionar ejercicios morfosintácticos guiados y evaluables.
* Visualizar el progreso individual del estudiante mediante métricas claras.
* Implementar un modelo de acceso ético (FREE / PREMIUM).
* Preparar la base técnica para futuras integraciones de IA educativa.

---

## 🧠 Fundamentación pedagógica

EduNomad se apoya en los siguientes principios:

* **Aprendizaje progresivo**: de estructuras simples a complejas.
* **Corrección explicada**: el error como oportunidad de aprendizaje.
* **Escritura contrastiva**: comparación entre el español y la lengua materna.
* **Autonomía del estudiante**: la IA como apoyo, no sustitución cognitiva.
* **Contextualización cultural**: ejemplos adaptados al entorno del aprendiz.

---

## 🏗️ Arquitectura del proyecto

El proyecto sigue una arquitectura modular basada en Django:

```
EduNomad/
├── config/           # Configuración global (settings, urls, wsgi)
├── core/             # Usuarios, perfiles, roles, dashboard
├── courses/          # Cursos, lecciones, niveles
├── practice/         # Ejercicios y prácticas morfosintácticas
├── solver/           # Lógica de resolución y corrección
├── subscription/     # Suscripciones y control de acceso (paywall)
├── media/            # Archivos subidos por usuarios
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📚 Modelo académico de aprendizaje

### Cursos

* Organizados por nivel (A1–C2)
* Cada curso contiene lecciones progresivas
* Ejemplo inicial: **Castellano A1 – Escritura básica**

### Lecciones

* Introducción teórica breve
* Ejemplos guiados
* Acceso gratuito a contenidos esenciales

### Ejercicios (Practice)

* Ejercicios morfosintácticos manuales
* Respuesta escrita o selección guiada
* Corrección inmediata o diferida

### Progreso

* Seguimiento individual por curso y lección
* Métricas de avance claras
* Base para análisis longitudinal

---

## 🔐 Monetización ética (Paywall)

EduNomad implementa un modelo de monetización ética mediante **decoradores de acceso**:

* **FREE**: acceso completo al aprendizaje esencial
* **PREMIUM**: herramientas avanzadas (análisis, feedback extendido, IA)

Este enfoque garantiza que **ningún estudiante quede excluido del aprendizaje básico**.

---

## 🤖 Integración futura de Inteligencia Artificial

La IA será incorporada progresivamente con fines pedagógicos:

* Análisis de errores morfosintácticos frecuentes
* Retroalimentación personalizada
* Ejercicios adaptativos según lengua materna
* Asistencia en reescritura guiada

La IA **no reemplaza al estudiante**, sino que acompaña su proceso cognitivo.

---

## 🌍 Proyección intercultural y multilingüe

El diseño contempla estudiantes cuya lengua materna sea:

* Mandarín
* Inglés
* Hindi
* Español
* Árabe
* Bengalí
* Portugués
* Ruso
* Urdu
* Francés

El enfoque contrastivo permitirá adaptar explicaciones y ejemplos.

---

## 🧪 Estado del proyecto

* ✅ Arquitectura base implementada
* ✅ Modelos académicos definidos
* ✅ Primer curso estructurado
* ✅ Control de versiones en GitHub
* 🚧 Integración IA (fase futura)
* 🚧 Despliegue en producción

---

## 👤 Autor

**Hernán Acevedo Mar**
Proyecto académico-tecnológico en desarrollo
Investigación en educación, lenguaje y software

---

## 📜 Licencia

Este proyecto se publica con fines educativos y de investigación. La licencia específica será definida en fases posteriores del desarrollo.

---

> EduNomad no es solo una plataforma: es un laboratorio pedagógico para la escritura consciente en lengua castellana.
 LISTA COMPLETA DE COMANDOS para cada uno de los scripts de tu plataforma EduNomad:

📋 COMANDOS COMPLETOS PARA CADA SCRIPT
📚 GESTIÓN DE RECURSOS Y DATOS
bash
# Importar recursos educativos masivos desde archivos HTML
python importar_recursos_masivos.py

# Importar recursos desde SQLite (alternativa)
python importar_recursos.py

# Verificar datos importados
python verificar_datos.py

# Migrar datos de SQLite a MySQL
python migrar_a_mysql.py

# Configurar MySQL automáticamente
./configurar_mysql.sh
🎓 GESTIÓN DE CURSOS
bash
# Generar 100 cursos nuevos basados en técnicas de redacción
python generar_100_cursos.py

# Crear cursos desde recursos existentes
python crear_cursos_masivos.py

# Sincronizar cursos con language_practice
python sincronizar_cursos.py
📝 GENERACIÓN DE CONTENIDO
bash
# Generar lecciones, prácticas y evaluaciones (versión original)
python generar_lecciones_practicas_evaluaciones.py

# Generar lecciones, prácticas y evaluaciones (versión corregida - RECOMENDADA)
python generar_lecciones_practicas_evaluaciones_corregido.py

# Generar 100 ejercicios por práctica/evaluación
python generar_100_ejercicios.py

# Generar ejercicios masivos (30 por entidad)
python generar_ejercicios_masivos.py

# Revisar y completar contenido faltante
python revisar_y_completar_contenido.py
🏅 GAMIFICACIÓN Y CERTIFICACIONES
bash
# Inicializar insignias del sistema
python inicializar_insignias.py

# Generar certificados masivos
python crear_certificados_masivos.py

# Probar sistema de certificaciones
python probar_certificaciones.py

# Generar prácticas y evaluaciones con gamificación
python generar_practicas_evaluaciones.py
👥 GESTIÓN DE USUARIOS
bash
# Gestionar roles de usuarios (Superusuario, Profesor, Estudiante)
python gestion_roles.py

# Gestionar roles (versión corregida - RECOMENDADA)
python gestion_roles_corregido.py

# Registrar estudiantes masivos desde CSV
python registrar_estudiantes_masivos.py

# Verificar credenciales de usuarios
python verificar_credenciales.py
💬 MENSAJERÍA
bash
# Sistema de mensajería entre profesores y estudiantes
python sistema_mensajeria.py
🧪 PRUEBAS Y VERIFICACIÓN
bash
# Prueba completa del sistema (más completa)
python prueba_completa.py

# Prueba del sistema (alternativa)
python prueba_sistema.py

# Verificar prácticas y evaluaciones
python verificar_practicas_evaluaciones.py

# Verificar credenciales
python verificar_credenciales.py
🔧 SCRIPTS DE GENERACIÓN
bash
# Generar certificados (script)
python crear_certificados_masivos.py

# Generar evaluaciones masivas
python crear_evaluaciones_masivas.py

# Generar lecciones (corregido)
python crear_lecciones_corregido.py

# Generar lecciones masivas
python crear_lecciones_masivas.py

# Generar prácticas previas
python crear_practicas_previas.py

# Configuración completa (script unificado)
python setup_completo.py
📁 SCRIPTS SHELL (SH)
bash
# Generar certificados
./generar_certificados.sh

# Generar evaluaciones
./generar_evaluaciones.sh

# Generar lecciones
./generar_lecciones.sh

# Generar prácticas previas
./generar_practicas_previas.sh
📊 COMANDOS DE VERIFICACIÓN
bash
# Verificar estado del sistema
python manage.py check

# Ver todas las URLs
python manage.py show_urls

# Ver migraciones
python manage.py showmigrations

# Ver base de datos actual
python manage.py shell -c "
from django.db import connection
print(f'Base: {connection.settings_dict[\"NAME\"]}')
print(f'Motor: {connection.settings_dict[\"ENGINE\"]}')
"

# Ver estadísticas completas
python manage.py shell -c "
from apps.core.models import Curso, Practica, Evaluacion, EjercicioInteractivo, RecursoEducativo
print('=' * 50)
print('📊 ESTADÍSTICAS')
print('=' * 50)
print(f'Cursos: {Curso.objects.count()}')
print(f'Prácticas: {Practica.objects.count()}')
print(f'Evaluaciones: {Evaluacion.objects.count()}')
print(f'Ejercicios: {EjercicioInteractivo.objects.count()}')
print(f'Recursos: {RecursoEducativo.objects.count()}')
"
🚀 SERVIDOR Y DESPLIEGUE
bash
# Iniciar servidor de desarrollo
python manage.py runserver

# Iniciar en puerto específico
python manage.py runserver 8001

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Verificar configuración de producción
python manage.py check --deploy
📋 COMANDOS DE MANTENIMIENTO
Limpieza y respaldo
bash
# Limpiar caché de Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Hacer backup de la base de datos (SQLite)
sqlite3 db.sqlite3 ".backup db_backup_$(date +%Y%m%d).sqlite3"

# Hacer backup de MySQL
sudo mysqldump -u root edunomad_db > edunomad_backup_$(date +%Y%m%d).sql

# Ver logs de Django
tail -f logs/django.log

# Ver tráfico de la base de datos
sudo mysql -e "SHOW PROCESSLIST;"
Git y control de versiones
bash
# Ver estado
git status

# Ver cambios
git diff

# Ver historial
git log --oneline -10

# Agregar todos los cambios
git add -A

# Commit
git commit -m "Descripción del cambio"

# Subir a GitHub
git push origin main

# Traer cambios
git pull origin main
📋 COMANDOS DE SOLUCIÓN DE PROBLEMAS
MySQL
bash
# Iniciar MySQL
sudo service mysql start

# Detener MySQL
sudo service mysql stop

# Reiniciar MySQL
sudo service mysql restart

# Ver estado
sudo service mysql status

# Acceder a MySQL
sudo mysql -u root

# Ver bases de datos
sudo mysql -e "SHOW DATABASES;"

# Usar base de datos
sudo mysql -e "USE edunomad_db; SHOW TABLES;"

# Ver tamaño de base de datos
sudo mysql -e "SELECT table_schema AS 'Database', 
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' 
    FROM information_schema.tables 
    WHERE table_schema = 'edunomad_db' 
    GROUP BY table_schema;"
Django
bash
# Verificar errores del sistema
python manage.py check

# Recrear migraciones
python manage.py makemigrations
python manage.py migrate

# Forzar migración
python manage.py migrate --fake-initial

# Resetear base de datos (cuidado!)
python manage.py flush

# Crear superusuario (si no existe)
python manage.py createsuperuser
📋 COMANDOS PARA PRUEBAS
bash
# Prueba completa del sistema
python prueba_completa.py

# Prueba de API
curl http://localhost:8000/api/recursos/ | python -m json.tool

# Prueba de cursos
curl http://localhost:8000/api/cursos/ | python -m json.tool

# Prueba de estadísticas
curl http://localhost:8000/api/recursos/estadisticas/ | python -m json.tool

# Prueba de autenticación
curl -X POST http://localhost:8000/login/ -d "username=test&password=test123"
📋 GUARDAR ESTA LISTA
bash
cat > comandos_completos.md << 'EOF'
# COMANDOS COMPLETOS PARA EDUNOMAD

[Pega aquí toda la lista de comandos]
EOF

# Ver el archivo
cat comandos_completos.md
¡COMANDOS COMPLETOS DISPONIBLES! 🚀📋
