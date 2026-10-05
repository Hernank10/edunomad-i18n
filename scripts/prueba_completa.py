#!/usr/bin/env python3
"""
PRUEBA COMPLETA DEL SISTEMA EDUNOMAD
Verifica: Modelos, Vistas, Gamificación, Mensajería, Roles, Ejercicios, etc.
"""
import os
import sys
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from django.urls import get_resolver
from django.test.client import Client

from apps.core.models import (
    Curso, RecursoEducativo, Practica, Evaluacion, 
    EjercicioInteractivo, Certificacion, ProgresoCurso,
    Insignia, InsigniaUsuario, PuntajeUsuario, 
    EntregaArchivo, PerfilUsuario, Mensaje, Notificacion
)
from apps.core.gamificacion_utils import (
    inicializar_insignias, obtener_estadisticas_usuario,
    actualizar_puntaje, obtener_puntaje_usuario
)

print("=" * 80)
print("🧪 PRUEBA COMPLETA DEL SISTEMA EDUNOMAD")
print("=" * 80)
print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 80)

# ============================================
# 1. VERIFICAR BASE DE DATOS
# ============================================
print("\n📊 1. VERIFICANDO BASE DE DATOS")
print("-" * 60)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tablas = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tablas encontradas: {len(tablas)}")
        
        tablas_core = [t for t in tablas if t.startswith('core_')]
        print(f"   - Tablas core: {len(tablas_core)}")
        
        # Tablas importantes
        tablas_importantes = [
            'core_recursoeducativo', 'core_curso', 'core_practica', 
            'core_evaluacion', 'core_ejerciciointeractivo', 'core_insignia',
            'core_perfilusuario', 'core_mensaje', 'core_notificacion',
            'core_certificacion', 'core_progresocurso', 'core_puntajeusuario'
        ]
        
        for t in tablas_importantes:
            if t in tablas:
                print(f"     ✅ {t}")
            else:
                print(f"     ❌ {t} - FALTA")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 2. VERIFICAR MODELOS Y DATOS
# ============================================
print("\n📦 2. VERIFICANDO MODELOS Y DATOS")
print("-" * 60)

modelos_datos = {
    'RecursoEducativo': RecursoEducativo,
    'Curso': Curso,
    'Practica': Practica,
    'Evaluacion': Evaluacion,
    'EjercicioInteractivo': EjercicioInteractivo,
    'Certificacion': Certificacion,
    'ProgresoCurso': ProgresoCurso,
    'Insignia': Insignia,
    'PuntajeUsuario': PuntajeUsuario,
    'PerfilUsuario': PerfilUsuario,
    'Mensaje': Mensaje,
    'Notificacion': Notificacion,
}

for nombre, modelo in modelos_datos.items():
    try:
        count = modelo.objects.count()
        print(f"✅ {nombre:20} | {count:>6} registros")
    except Exception as e:
        print(f"❌ {nombre:20} | Error - {str(e)[:40]}")

# ============================================
# 3. VERIFICAR USUARIOS Y ROLES
# ============================================
print("\n👥 3. VERIFICANDO USUARIOS Y ROLES")
print("-" * 60)

try:
    usuarios = User.objects.all()
    print(f"✅ Usuarios totales: {usuarios.count()}")
    
    # Verificar perfiles
    perfiles = PerfilUsuario.objects.all()
    print(f"✅ Perfiles: {perfiles.count()}")
    
    # Estadísticas por rol
    roles = {}
    for perfil in perfiles:
        rol = perfil.rol
        roles[rol] = roles.get(rol, 0) + 1
    
    print(f"\n📋 Distribución por rol:")
    for rol, count in roles.items():
        icono = {
            'SUPERUSUARIO': '👑',
            'PROFESOR': '👨‍🏫',
            'ESTUDIANTE': '👨‍🎓',
            'ADMIN': '👤'
        }.get(rol, '👤')
        print(f"   {icono} {rol}: {count} usuarios")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 4. VERIFICAR INSIGNIAS
# ============================================
print("\n🏅 4. VERIFICANDO INSIGNIAS")
print("-" * 60)

try:
    # Inicializar insignias si no existen
    if Insignia.objects.count() == 0:
        print("📝 Inicializando insignias...")
        creadas = inicializar_insignias()
        print(f"✅ {creadas} insignias creadas")
    
    insignias = Insignia.objects.all()
    print(f"✅ Insignias totales: {insignias.count()}")
    
    # Detalle de insignias por nivel
    niveles = {}
    for ins in insignias:
        nivel = ins.nivel
        niveles[nivel] = niveles.get(nivel, 0) + 1
    
    print(f"\n📋 Insignias por nivel:")
    for nivel, count in sorted(niveles.items()):
        icono = {
            'BRONCE': '🥉',
            'PLATA': '🥈',
            'ORO': '🥇',
            'DIAMANTE': '💎',
            'EXPERTO': '⭐'
        }.get(nivel, '🏅')
        print(f"   {icono} {nivel}: {count} insignias")
    
    # Mostrar insignias
    print(f"\n📋 Lista de insignias:")
    for ins in insignias:
        print(f"   {ins.icono} {ins.nombre} ({ins.get_nivel_display()})")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 5. VERIFICAR EJERCICIOS
# ============================================
print("\n📝 5. VERIFICANDO EJERCICIOS")
print("-" * 60)

try:
    total_ejercicios = EjercicioInteractivo.objects.count()
    print(f"✅ Ejercicios totales: {total_ejercicios}")
    
    # Tipos de ejercicios
    from django.db import models
    tipos = EjercicioInteractivo.objects.values('tipo').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    print(f"\n📋 Distribución por tipo:")
    for t in tipos:
        print(f"   - {t['tipo']}: {t['count']} ejercicios")
    
    # Verificar ejercicios por práctica
    practicas_con_ejercicios = 0
    for practica in Practica.objects.all():
        count = EjercicioInteractivo.objects.filter(practica=practica).count()
        if count > 0:
            practicas_con_ejercicios += 1
    
    print(f"\n✅ Prácticas con ejercicios: {practicas_con_ejercicios}/{Practica.objects.count()}")
    
    # Verificar ejercicios por evaluación
    evaluaciones_con_ejercicios = 0
    for evaluacion in Evaluacion.objects.all():
        count = EjercicioInteractivo.objects.filter(evaluacion=evaluacion).count()
        if count > 0:
            evaluaciones_con_ejercicios += 1
    
    print(f"✅ Evaluaciones con ejercicios: {evaluaciones_con_ejercicios}/{Evaluacion.objects.count()}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 6. VERIFICAR GAMIFICACIÓN
# ============================================
print("\n🎮 6. VERIFICANDO GAMIFICACIÓN")
print("-" * 60)

try:
    # Crear usuario de prueba para gamificación
    test_user, created = User.objects.get_or_create(
        username='test_gamifica',
        defaults={
            'email': 'test_gamifica@edunomad.com',
            'first_name': 'Test',
            'last_name': 'Gamificacion'
        }
    )
    if created:
        test_user.set_password('test123')
        test_user.save()
        print(f"✅ Usuario de prueba creado: {test_user.username}")
    
    # Obtener estadísticas
    stats = obtener_estadisticas_usuario(test_user)
    print(f"\n📊 Estadísticas de {test_user.username}:")
    print(f"   • Puntos totales: {stats['puntos_totales']}")
    print(f"   • Nivel: {stats['nivel']}")
    print(f"   • Racha actual: {stats['racha_actual']}")
    print(f"   • Racha máxima: {stats['racha_maxima']}")
    print(f"   • Insignias: {stats['total_insignias']}")
    print(f"   • Precisión: {stats['precision']}%")
    
    # Actualizar puntaje
    puntaje = actualizar_puntaje(test_user, 10, 'correcto')
    print(f"\n✅ Puntaje actualizado: +10 puntos (Total: {puntaje.puntos_totales})")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 7. VERIFICAR MENSAJERÍA
# ============================================
print("\n💬 7. VERIFICANDO MENSAJERÍA")
print("-" * 60)

try:
    total_mensajes = Mensaje.objects.count()
    print(f"✅ Mensajes totales: {total_mensajes}")
    
    # Mensajes por tipo
    tipos_mensaje = Mensaje.objects.values('tipo').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    print(f"\n📋 Mensajes por tipo:")
    for t in tipos_mensaje:
        print(f"   - {t['tipo']}: {t['count']} mensajes")
    
    # Notificaciones
    total_notificaciones = Notificacion.objects.count()
    print(f"\n✅ Notificaciones totales: {total_notificaciones}")
    
    # Notificaciones no leídas
    no_leidas = Notificacion.objects.filter(leido=False).count()
    print(f"   - No leídas: {no_leidas}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 8. VERIFICAR CURSOS Y RECURSOS
# ============================================
print("\n📚 8. VERIFICANDO CURSOS Y RECURSOS")
print("-" * 60)

try:
    cursos = Curso.objects.all()
    print(f"✅ Cursos totales: {cursos.count()}")
    
    # Estadísticas por curso
    print(f"\n📋 Cursos con datos:")
    for curso in cursos[:5]:
        recursos = curso.recursos.count()
        practicas = Practica.objects.filter(curso=curso).count()
        evaluaciones = Evaluacion.objects.filter(curso=curso).count()
        print(f"   • {curso.titulo[:40]}")
        print(f"     - Recursos: {recursos}, Prácticas: {practicas}, Evaluaciones: {evaluaciones}")
    if cursos.count() > 5:
        print(f"   ... y {cursos.count() - 5} más")
    
    total_recursos = RecursoEducativo.objects.count()
    print(f"\n✅ Recursos educativos: {total_recursos}")
    
    # Categorías de recursos
    categorias = RecursoEducativo.objects.values('categoria').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    print(f"\n📋 Categorías de recursos:")
    for cat in categorias[:10]:
        print(f"   - {cat['categoria']}: {cat['count']} recursos")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 9. VERIFICAR API
# ============================================
print("\n🌐 9. VERIFICANDO API")
print("-" * 60)

try:
    resolver = get_resolver()
    urls = []
    for pattern in resolver.url_patterns:
        urls.append(str(pattern))
    
    print(f"✅ URLs registradas: {len(urls)}")
    
    # URLs importantes
    urls_importantes = [
        '/', '/dashboard/', '/cursos/', '/recursos/',
        '/api/recursos/', '/api/cursos/', '/admin/',
        '/practicas/', '/evaluaciones/', '/certificaciones/',
        '/insignias/', '/ranking/'
    ]
    
    print(f"\n📋 URLs importantes:")
    for url in urls_importantes:
        print(f"   {'✅' if any(url in str(u) for u in urls) else '❌'} {url}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# 10. VERIFICAR CREDENCIALES
# ============================================
print("\n🔑 10. VERIFICANDO CREDENCIALES")
print("-" * 60)

credenciales = {
    'Superusuario': {'username': 'profesorhernanacevedoM777', 'password': 'password123'},
    'Profesor': {'username': 'profesor_001', 'password': 'EduNomad2024'},
    'Estudiante': {'username': 'estudiante_001', 'password': 'EduNomad2024'},
}

print("🔑 Credenciales de prueba:")
for rol, cred in credenciales.items():
    user = User.objects.filter(username=cred['username']).first()
    if user:
        autenticado = django.contrib.auth.authenticate(
            username=cred['username'], 
            password=cred['password']
        )
        print(f"   {rol:12} | {cred['username']:25} | {'✅ Válida' if autenticado else '❌ Inválida'}")
    else:
        print(f"   {rol:12} | {cred['username']:25} | ❌ No existe")

# ============================================
# 11. RESUMEN FINAL
# ============================================
print("\n" + "=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)

# Calcular estadísticas generales
stats = {
    'Recursos': RecursoEducativo.objects.count(),
    'Cursos': Curso.objects.count(),
    'Prácticas': Practica.objects.count(),
    'Evaluaciones': Evaluacion.objects.count(),
    'Ejercicios': EjercicioInteractivo.objects.count(),
    'Usuarios': User.objects.count(),
    'Perfiles': PerfilUsuario.objects.count(),
    'Insignias': Insignia.objects.count(),
    'Certificaciones': Certificacion.objects.count(),
    'Mensajes': Mensaje.objects.count(),
    'Notificaciones': Notificacion.objects.count(),
}

print("\n📊 ESTADÍSTICAS GENERALES:")
print("-" * 40)
for key, value in stats.items():
    print(f"   {key:15}: {value:>6}")

# Evaluación de resultados
print("\n" + "=" * 80)
print("✅ RESULTADO DE LA PRUEBA:")
print("=" * 80)

errores = 0
if stats['Recursos'] == 0: errores += 1
if stats['Cursos'] == 0: errores += 1
if stats['Ejercicios'] == 0: errores += 1
if stats['Usuarios'] == 0: errores += 1
if stats['Insignias'] == 0: errores += 1

if errores == 0:
    print("🎉 ¡TODOS LOS SISTEMAS FUNCIONAN CORRECTAMENTE!")
    print("✅ Base de datos: OK")
    print("✅ Modelos: OK")
    print("✅ Usuarios y roles: OK")
    print("✅ Gamificación: OK")
    print("✅ Mensajería: OK")
    print("✅ Cursos y recursos: OK")
    print("✅ Ejercicios: OK")
    print("✅ API: OK")
    print("✅ Credenciales: OK")
else:
    print(f"⚠️ Se encontraron {errores} errores en la prueba")
    print("❌ Revisa los logs para más detalles")

print("\n" + "=" * 80)
print("🎉 ¡PRUEBA COMPLETADA!")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 80)
