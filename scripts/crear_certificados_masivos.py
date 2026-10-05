#!/usr/bin/env python3
"""
Script para generar certificados automáticos para usuarios que completan cursos
"""
import os
import random
import hashlib
import time
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso, Certificado, Logro, LogroUsuario
from django.contrib.auth.models import User

print("📜 GENERANDO CERTIFICADOS Y LOGROS")
print("=" * 60)

# Verificar usuarios
usuarios = User.objects.all()
if usuarios.count() == 0:
    print("⚠️ No hay usuarios registrados. Creando usuarios de prueba...")
    # Crear usuarios de prueba
    usuarios_creados = 0
    for i in range(5):
        username = f"estudiante_{i+1}"
        email = f"estudiante{i+1}@example.com"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123"
            )
            user.first_name = f"Estudiante {i+1}"
            user.last_name = f"Apellido {i+1}"
            user.save()
            usuarios_creados += 1
    
    print(f"✅ {usuarios_creados} usuarios de prueba creados")
    usuarios = User.objects.all()

print(f"👤 Usuarios encontrados: {usuarios.count()}")

# Obtener cursos
cursos = Curso.objects.all()
print(f"🎓 Cursos encontrados: {cursos.count()}")

if cursos.count() == 0:
    print("❌ No hay cursos. Primero crea cursos.")
    exit()

# Crear logros si no existen
logros_data = [
    {"nombre": "Primer Curso Completado", "descripcion": "Completaste tu primer curso", "tipo": "CURSO", "icono": "fa-graduation-cap", "color": "#4F46E5", "puntos": 50},
    {"nombre": "Estudiante Constante", "descripcion": "Completaste 3 cursos", "tipo": "CURSO", "icono": "fa-book", "color": "#10B981", "puntos": 100},
    {"nombre": "Experto", "descripcion": "Completaste 5 cursos", "tipo": "CURSO", "icono": "fa-star", "color": "#F59E0B", "puntos": 200},
    {"nombre": "Evaluador", "descripcion": "Aprobaste una evaluación", "tipo": "EVALUACION", "icono": "fa-check-circle", "color": "#3B82F6", "puntos": 30},
    {"nombre": "Práctico", "descripcion": "Completaste una práctica previa", "tipo": "PRACTICA", "icono": "fa-tasks", "color": "#8B5CF6", "puntos": 20},
]

for data in logros_data:
    logro, created = Logro.objects.get_or_create(
        nombre=data["nombre"],
        defaults={
            "descripcion": data["descripcion"],
            "tipo": data["tipo"],
            "icono": data["icono"],
            "color": data["color"],
            "puntos": data["puntos"],
            "is_active": True,
        }
    )
    if created:
        print(f"  🏆 Logro creado: {logro.nombre}")

print(f"🏆 Logros disponibles: {Logro.objects.count()}")

# Datos para generar certificados
nombres_titulos = [
    "Excelencia Académica", "Desempeño Sobresaliente", "Aprendizaje Continuo",
    "Dominio del Tema", "Habilidades Avanzadas", "Compromiso con el Aprendizaje",
    "Logro Destacado", "Trayectoria Exitosa"
]

habilidades_por_categoria = {
    'sintaxis': ['Análisis Sintáctico', 'Estructura de Oraciones', 'Morfosintaxis'],
    'gramatica': ['Gramática Avanzada', 'Morfología', 'Conjugación Verbal'],
    'redaccion': ['Redacción Técnica', 'Escritura Creativa', 'Composición'],
    'ortografia': ['Ortografía Avanzada', 'Puntuación', 'Corrección de Textos'],
    'retorica': ['Argumentación', 'Persuasión', 'Discurso'],
    'narrativa': ['Narrativa', 'Cuento', 'Personajes'],
    'literatura': ['Literatura Hispanoamericana', 'Poesía', 'Análisis Literario'],
    'ciencia_ficcion': ['Ciencia Ficción', 'Mundos Futuristas', 'Tecnología'],
    'general': ['Lengua Castellana', 'Comunicación', 'Redacción Avanzada']
}

def generar_habilidades(categoria):
    """Genera habilidades según la categoría del curso"""
    return random.choice(list(habilidades_por_categoria.values()))

def generar_descripcion(curso, usuario, puntaje):
    """Genera descripción personalizada del certificado"""
    templates = [
        f"Certifica que {usuario.first_name or usuario.username} ha completado exitosamente el curso '{curso.titulo}' con un puntaje de {puntaje}%.",
        f"Por su destacado desempeño en el curso '{curso.titulo}', se otorga este certificado a {usuario.first_name or usuario.username}.",
        f"{usuario.first_name or usuario.username} ha demostrado dominio en '{curso.titulo}' con una calificación del {puntaje}%.",
    ]
    return random.choice(templates)

print("\n🔄 Generando certificados...")
certificados_creados = 0
errores = 0

for curso in cursos:
    # Seleccionar usuarios aleatorios para este curso (50-80% de los usuarios)
    num_usuarios = random.randint(1, max(1, usuarios.count() // 2))
    usuarios_curso = random.sample(list(usuarios), min(num_usuarios, len(usuarios)))
    
    if not usuarios_curso:
        continue
    
    print(f"\n📖 Curso: {curso.titulo}")
    print(f"   Usuarios: {len(usuarios_curso)}")
    
    for usuario in usuarios_curso:
        try:
            # Determinar si completó el curso (70% de probabilidad)
            completado = random.random() < 0.7
            
            if not completado:
                continue
            
            # Generar puntaje aleatorio (60-100%)
            puntaje = random.randint(60, 100)
            
            # Fechas
            fecha_inicio = datetime.now() - timedelta(days=random.randint(10, 60))
            fecha_completado = fecha_inicio + timedelta(days=random.randint(5, 30))
            
            # Generar código único
            codigo = hashlib.sha256(f"{usuario.id}-{curso.id}-{time.time()}".encode()).hexdigest()[:16].upper()
            
            # Crear certificado
            certificado, created = Certificado.objects.get_or_create(
                usuario=usuario,
                curso=curso,
                tipo='CURSO',
                defaults={
                    'estado': 'GENERADO',
                    'nombre_completo': f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username,
                    'identificacion': f"ID-{usuario.id:06d}",
                    'puntaje_obtenido': puntaje,
                    'porcentaje': puntaje,
                    'fecha_inicio': fecha_inicio,
                    'fecha_completado': fecha_completado,
                    'fecha_vencimiento': fecha_completado + timedelta(days=365),
                    'codigo_verificacion': codigo,
                    'descripcion': generar_descripcion(curso, usuario, puntaje),
                    'habilidades': generar_habilidades(curso.categoria.lower()),
                    'is_active': True,
                }
            )
            
            if created:
                certificados_creados += 1
                print(f"   ✅ {usuario.username}: {certificado.nombre_completo} - {puntaje}%")
                
                # Otorgar logros automáticamente
                # Logro: Primer curso completado
                logro_primer = Logro.objects.filter(nombre="Primer Curso Completado").first()
                if logro_primer and not LogroUsuario.objects.filter(usuario=usuario, logro=logro_primer).exists():
                    LogroUsuario.objects.create(usuario=usuario, logro=logro_primer)
                    print(f"      🏆 Logro obtenido: {logro_primer.nombre}")
                
                # Logro: Experto (5 cursos)
                cursos_completados = Certificado.objects.filter(usuario=usuario, tipo='CURSO', estado='GENERADO').count()
                if cursos_completados >= 5:
                    logro_experto = Logro.objects.filter(nombre="Experto").first()
                    if logro_experto and not LogroUsuario.objects.filter(usuario=usuario, logro=logro_experto).exists():
                        LogroUsuario.objects.create(usuario=usuario, logro=logro_experto)
                        print(f"      🏆 Logro obtenido: {logro_experto.nombre}")
                
                # Logro: Estudiante Constante (3 cursos)
                if cursos_completados >= 3 and cursos_completados < 5:
                    logro_constante = Logro.objects.filter(nombre="Estudiante Constante").first()
                    if logro_constante and not LogroUsuario.objects.filter(usuario=usuario, logro=logro_constante).exists():
                        LogroUsuario.objects.create(usuario=usuario, logro=logro_constante)
                        print(f"      🏆 Logro obtenido: {logro_constante.nombre}")
                
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"   ❌ Error con {usuario.username}: {e}")

print("\n" + "=" * 60)
print(f"🎉 {certificados_creados} certificados creados exitosamente")
if errores > 0:
    print(f"⚠️ {errores} errores encontrados")
print(f"📊 Total certificados: {Certificado.objects.count()}")

# Mostrar resumen por curso
print("\n📋 RESUMEN POR CURSO:")
for curso in cursos:
    count = Certificado.objects.filter(curso=curso, estado='GENERADO').count()
    if count > 0:
        print(f"  - {curso.titulo[:40]}: {count} certificados")

# Mostrar logros otorgados
print("\n🏆 LOGROS OTORGADOS:")
for logro in Logro.objects.all():
    count = LogroUsuario.objects.filter(logro=logro).count()
    if count > 0:
        print(f"  - {logro.nombre}: {count} usuarios")

print("\n📊 RESUMEN GENERAL:")
print(f"  - Certificados: {Certificado.objects.count()}")
print(f"  - Logros disponibles: {Logro.objects.count()}")
print(f"  - Logros otorgados: {LogroUsuario.objects.count()}")
