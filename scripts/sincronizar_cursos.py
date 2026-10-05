#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Curso as CoreCurso
from apps.language_practice.models import Course

print("🔄 SINCRONIZANDO CURSOS...")

cursos_creados = 0
for core_curso in CoreCurso.objects.all():
    curso_lp, created = Course.objects.get_or_create(
        title=core_curso.titulo,
        defaults={
            'description': core_curso.descripcion or f"Curso de {core_curso.categoria}",
            'language': core_curso.categoria.lower(),
            'level': core_curso.nivel.lower() if core_curso.nivel else 'intermediate',
            'is_active': True,
        }
    )
    if created:
        cursos_creados += 1
        print(f"  ✅ {core_curso.titulo}")

print(f"✅ {cursos_creados} cursos sincronizados")
print(f"📊 Total cursos en language_practice: {Course.objects.count()}")
