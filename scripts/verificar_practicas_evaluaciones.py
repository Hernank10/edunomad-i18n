#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Practica, Evaluacion, EjercicioInteractivo
from apps.core.models import Curso

print("📊 VERIFICANDO PRÁCTICAS Y EVALUACIONES")
print("=" * 50)

print(f"📝 Prácticas totales: {Practica.objects.count()}")
print(f"📝 Evaluaciones totales: {Evaluacion.objects.count()}")
print(f"📝 Ejercicios totales: {EjercicioInteractivo.objects.count()}")

print("\n📋 PRÁCTICAS POR CURSO:")
for curso in Curso.objects.all():
    count = Practica.objects.filter(curso=curso).count()
    if count > 0:
        print(f"  - {curso.titulo[:40]}: {count} prácticas")

print("\n📋 EVALUACIONES POR CURSO:")
for curso in Curso.objects.all():
    count = Evaluacion.objects.filter(curso=curso).count()
    if count > 0:
        print(f"  - {curso.titulo[:40]}: {count} evaluaciones")
