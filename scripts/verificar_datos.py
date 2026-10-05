#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import RecursoEducativo, Curso
from apps.language_practice.models import Course, Lesson

print("📊 DATOS ACTUALES:")
print("=" * 50)
print(f"📚 Recursos (core): {RecursoEducativo.objects.count()}")
print(f"🎓 Cursos (core): {Curso.objects.count()}")
print(f"🎓 Cursos (language_practice): {Course.objects.count()}")
print(f"📖 Lecciones (language_practice): {Lesson.objects.count()}")

print("\n📋 ÚLTIMOS CURSOS (core):")
for curso in Curso.objects.all().order_by('-id')[:5]:
    print(f"  - {curso.titulo} ({curso.categoria}) - {curso.nivel}")

print("\n📋 ÚLTIMOS CURSOS (language_practice):")
for curso in Course.objects.all().order_by('-id')[:5]:
    lecciones = Lesson.objects.filter(course=curso).count()
    print(f"  - {curso.title} ({curso.language}) - {lecciones} lecciones")
