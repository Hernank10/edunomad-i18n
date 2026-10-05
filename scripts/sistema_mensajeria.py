#!/usr/bin/env python3
"""
Sistema de mensajería entre profesores y estudiantes
"""
import os
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from apps.core.models import PerfilUsuario, Curso, Mensaje, Notificacion

print("=" * 70)
print("💬 SISTEMA DE MENSAJERÍA")
print("=" * 70)

# ============================================
# 1. ENVIAR MENSAJE DE PRUEBA
# ============================================
def enviar_mensaje(remitente_username, destinatario_username, asunto, contenido):
    """Envía un mensaje entre usuarios"""
    try:
        remitente = User.objects.get(username=remitente_username)
        destinatario = User.objects.get(username=destinatario_username)
        
        mensaje = Mensaje.objects.create(
            remitente=remitente,
            destinatario=destinatario,
            asunto=asunto,
            contenido=contenido,
            tipo='PRIVADO',
        )
        
        # Crear notificación
        Notificacion.objects.create(
            usuario=destinatario,
            tipo='MENSAJE',
            titulo=f"Nuevo mensaje de {remitente.username}",
            contenido=contenido[:200],
        )
        
        print(f"✅ Mensaje enviado: {remitente.username} -> {destinatario.username}")
        return mensaje
        
    except User.DoesNotExist:
        print(f"❌ Usuario no encontrado")
        return None

# ============================================
# 2. ENVIAR MENSAJE A TODOS LOS ESTUDIANTES DE UN CURSO
# ============================================
def enviar_mensaje_grupal(profesor_username, curso_id, asunto, contenido):
    """Envía un mensaje a todos los estudiantes de un curso"""
    try:
        profesor = User.objects.get(username=profesor_username)
        curso = Curso.objects.get(id=curso_id)
        
        # Obtener estudiantes del curso
        estudiantes = PerfilUsuario.objects.filter(
            rol='ESTUDIANTE',
            cursos_inscritos=curso
        ).select_related('usuario')
        
        if not estudiantes:
            print(f"⚠️ No hay estudiantes inscritos en el curso {curso.titulo}")
            return
        
        for perfil in estudiantes:
            mensaje = Mensaje.objects.create(
                remitente=profesor,
                destinatario=perfil.usuario,
                curso=curso,
                asunto=asunto,
                contenido=f"[Curso: {curso.titulo}]\n{contenido}",
                tipo='GRUPO',
            )
            
            Notificacion.objects.create(
                usuario=perfil.usuario,
                tipo='MENSAJE',
                titulo=f"Mensaje del curso {curso.titulo}",
                contenido=contenido[:200],
            )
        
        print(f"✅ Mensaje enviado a {len(estudiantes)} estudiantes del curso {curso.titulo}")
        
    except User.DoesNotExist:
        print(f"❌ Profesor no encontrado")
    except Curso.DoesNotExist:
        print(f"❌ Curso no encontrado")

# ============================================
# 3. VER MENSAJES DE UN USUARIO
# ============================================
def ver_mensajes(username):
    """Ver mensajes recibidos por un usuario"""
    try:
        user = User.objects.get(username=username)
        mensajes = Mensaje.objects.filter(destinatario=user).order_by('-fecha_envio')
        
        print(f"\n📬 Mensajes de {username}:")
        print("-" * 50)
        
        if not mensajes:
            print("  No hay mensajes")
            return
        
        for m in mensajes[:10]:
            print(f"  📩 {m.remitente.username:20} | {m.asunto[:30]:30} | {m.tiempo_envio}")
            print(f"     {m.contenido[:80]}...")
            print("")
            
    except User.DoesNotExist:
        print(f"❌ Usuario no encontrado")

# ============================================
# 4. VER NOTIFICACIONES
# ============================================
def ver_notificaciones(username):
    """Ver notificaciones de un usuario"""
    try:
        user = User.objects.get(username=username)
        notificaciones = Notificacion.objects.filter(usuario=user, leido=False).order_by('-fecha_creacion')
        
        print(f"\n🔔 Notificaciones de {username}:")
        print("-" * 50)
        
        if not notificaciones:
            print("  No hay notificaciones pendientes")
            return
        
        for n in notificaciones:
            print(f"  🔔 {n.titulo}")
            print(f"     {n.contenido[:100]}...")
            print(f"     📅 {n.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
            print("")
            
    except User.DoesNotExist:
        print(f"❌ Usuario no encontrado")

# ============================================
# 5. EJECUTAR PRUEBAS
# ============================================
print("\n📝 1. ENVIANDO MENSAJES DE PRUEBA")

# Enviar mensaje de profesor a estudiante
enviar_mensaje(
    'profesor_001',
    'estudiante_001',
    'Bienvenido al curso',
    'Hola María, te damos la bienvenida al curso. Esperamos que disfrutes aprendiendo.'
)

enviar_mensaje(
    'profesor_002',
    'estudiante_002',
    'Consulta sobre la tarea',
    'Hola Carlos, ¿tienes alguna duda sobre la tarea de esta semana?'
)

# Enviar mensaje de estudiante a profesor
enviar_mensaje(
    'estudiante_003',
    'profesor_001',
    'Duda sobre el material',
    'Profesor, tengo una duda sobre el material de la clase 3. ¿Podría explicarlo nuevamente?'
)

print("\n📚 2. ENVIANDO MENSAJE GRUPAL")

# Enviar mensaje a todos los estudiantes de un curso
enviar_mensaje_grupal(
    'profesor_001',
    1,  # ID del curso
    'Recordatorio: Práctica para el viernes',
    'Recordatorio: La práctica de esta semana debe entregarse el viernes antes de las 23:59.'
)

print("\n👤 3. VERIFICANDO MENSAJES")

# Ver mensajes de varios usuarios
usuarios_prueba = ['profesor_001', 'estudiante_001', 'estudiante_003']

for username in usuarios_prueba:
    ver_mensajes(username)
    ver_notificaciones(username)

print("\n" + "=" * 70)
print("✅ SISTEMA DE MENSAJERÍA COMPLETADO")
print("=" * 70)
