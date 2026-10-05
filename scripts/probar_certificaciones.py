#!/usr/bin/env python3
"""
Script para probar el sistema de certificaciones
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Curso, Practica, Evaluacion, Certificacion, ProgresoCurso
from apps.core.certificacion_utils import verificar_certificacion, generar_certificacion

print("🧪 PROBANDO SISTEMA DE CERTIFICACIONES")
print("=" * 60)

# 1. Verificar usuarios
usuarios = User.objects.all()
if usuarios.count() == 0:
    print("❌ No hay usuarios. Creando usuario de prueba...")
    user = User.objects.create_user(
        username='test_user',
        email='test@test.com',
        password='test123'
    )
    user.first_name = 'Usuario'
    user.last_name = 'Prueba'
    user.save()
    usuarios = User.objects.all()
    print(f"✅ Usuario de prueba creado: {user.username}")

# 2. Verificar cursos
cursos = Curso.objects.all()
if cursos.count() == 0:
    print("❌ No hay cursos.")
    exit()

print(f"\n📚 Usuarios: {usuarios.count()}")
print(f"🎓 Cursos: {cursos.count()}")

# 3. Probar certificación para cada usuario y curso
print("\n📝 VERIFICANDO CERTIFICACIONES:")
for usuario in usuarios[:3]:  # Probar con los primeros 3 usuarios
    print(f"\n👤 Usuario: {usuario.username}")
    for curso in cursos[:3]:  # Probar con los primeros 3 cursos
        # Verificar certificación
        certificable, porcentaje = verificar_certificacion(usuario, curso)
        print(f"  📖 Curso: {curso.titulo[:30]}")
        print(f"     Completado: {porcentaje:.1f}%")
        print(f"     Certificable: {'✅ Sí' if certificable else '❌ No'}")
        
        if certificable:
            # Generar certificación
            certificacion, nueva = generar_certificacion(usuario, curso)
            print(f"     Certificación: {'✅ Nueva' if nueva else '⏳ Ya existente'}")
            print(f"     Código: {certificacion.codigo_verificacion}")

# 4. Estadísticas
print("\n📊 ESTADÍSTICAS FINALES:")
print(f"  📜 Certificaciones totales: {Certificacion.objects.count()}")
print(f"  📈 Progresos registrados: {ProgresoCurso.objects.count()}")
print(f"  ✅ Certificaciones completadas: {Certificacion.objects.filter(estado='COMPLETADO').count()}")

print("\n✅ Prueba completada!")
