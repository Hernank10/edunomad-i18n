#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Insignia

INSIGNIAS_PREDEFINIDAS = [
    {
        'nombre': 'Primer Paso',
        'descripcion': 'Completaste tu primera práctica',
        'tipo': 'PRACTICA',
        'nivel': 'BRONCE',
        'icono': 'fa-flag',
        'color': '#CD7F32',
        'puntos_requeridos': 10,
    },
    {
        'nombre': 'Estudiante Constante',
        'descripcion': 'Completaste 5 prácticas',
        'tipo': 'PRACTICA',
        'nivel': 'PLATA',
        'icono': 'fa-medal',
        'color': '#C0C0C0',
        'puntos_requeridos': 50,
    },
    {
        'nombre': 'Experto en Prácticas',
        'descripcion': 'Completaste 10 prácticas',
        'tipo': 'PRACTICA',
        'nivel': 'ORO',
        'icono': 'fa-trophy',
        'color': '#FFD700',
        'puntos_requeridos': 100,
    },
    {
        'nombre': 'Primera Evaluación',
        'descripcion': 'Completaste tu primera evaluación',
        'tipo': 'EVALUACION',
        'nivel': 'BRONCE',
        'icono': 'fa-check-circle',
        'color': '#CD7F32',
        'puntos_requeridos': 20,
    },
    {
        'nombre': 'Evaluador Experto',
        'descripcion': 'Completaste 5 evaluaciones',
        'tipo': 'EVALUACION',
        'nivel': 'PLATA',
        'icono': 'fa-star',
        'color': '#C0C0C0',
        'puntos_requeridos': 100,
    },
    {
        'nombre': 'Curso Completado',
        'descripcion': 'Completaste un curso completo',
        'tipo': 'CURSO',
        'nivel': 'ORO',
        'icono': 'fa-graduation-cap',
        'color': '#FFD700',
        'puntos_requeridos': 200,
    },
    {
        'nombre': 'Racha de Oro',
        'descripcion': 'Mantuviste una racha de 7 días',
        'tipo': 'RACHA',
        'nivel': 'DIAMANTE',
        'icono': 'fa-fire',
        'color': '#B9F2FF',
        'puntos_requeridos': 50,
    },
    {
        'nombre': 'Maestro Certificado',
        'descripcion': 'Obtuviste una certificación',
        'tipo': 'CERTIFICACION',
        'nivel': 'DIAMANTE',
        'icono': 'fa-certificate',
        'color': '#B9F2FF',
        'puntos_requeridos': 150,
    },
]

creadas = 0
for data in INSIGNIAS_PREDEFINIDAS:
    insignia, created = Insignia.objects.get_or_create(
        nombre=data['nombre'],
        defaults={
            'descripcion': data['descripcion'],
            'tipo': data['tipo'],
            'nivel': data['nivel'],
            'icono': data['icono'],
            'color': data['color'],
            'puntos_requeridos': data['puntos_requeridos'],
            'is_active': True,
        }
    )
    if created:
        creadas += 1
        print(f"🏅 Creada: {insignia.nombre}")

print(f"\n✅ {creadas} insignias creadas")
print(f"📊 Total insignias: {Insignia.objects.count()}")
