#!/usr/bin/env python3
import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import RecursoEducativo, Curso

print("🎓 CREANDO CURSOS DESDE RECURSOS IMPORTADOS")
print("=" * 60)

total_recursos = RecursoEducativo.objects.count()
print(f"📚 Recursos disponibles: {total_recursos}")

if total_recursos == 0:
    print("❌ No hay recursos. Importa primero.")
    exit()

# Obtener categorías
categorias = RecursoEducativo.objects.values_list('categoria', flat=True).distinct()
print(f"📂 Categorías: {list(categorias)}")

niveles = ['PRIMARIA', 'SECUNDARIA', 'BACHILLERATO', 'UNIVERSITARIO', 'POSGRADO']
estados = ['BORRADOR', 'PUBLICADO']

cursos_creados = 0
for categoria in categorias:
    recursos = list(RecursoEducativo.objects.filter(categoria=categoria))
    if len(recursos) < 3:
        print(f"⚠️ {categoria}: solo {len(recursos)} recursos")
        num_cursos = 1
    else:
        num_cursos = min(3, len(recursos) // 2)
    
    for i in range(num_cursos):
        num_recursos = min(4 + i, len(recursos))
        recursos_seleccionados = random.sample(recursos, num_recursos)
        
        if i == 0:
            titulo = f"Introducción a {categoria}"
        elif i == 1:
            titulo = f"{categoria} Intermedio"
        else:
            titulo = f"{categoria} Avanzado"
        
        curso, created = Curso.objects.get_or_create(
            titulo=titulo,
            defaults={
                "descripcion": f"Curso de {categoria} con {num_recursos} recursos prácticos.",
                "categoria": categoria,
                "nivel": random.choice(niveles),
                "estado": random.choice(estados),
                "duracion_horas": random.randint(10, 30),
                "palabras_clave": f"{categoria.lower()}, aprendizaje, educación",
                "precio": round(random.uniform(0, 99.99), 2),
            }
        )
        
        if created:
            curso.recursos.add(*recursos_seleccionados)
            cursos_creados += 1
            print(f"✅ {titulo} ({categoria}) - {num_recursos} recursos")

print(f"\n🎉 {cursos_creados} cursos creados")
print(f"📊 Total recursos: {RecursoEducativo.objects.count()}")
print(f"📊 Total cursos: {Curso.objects.count()}")
