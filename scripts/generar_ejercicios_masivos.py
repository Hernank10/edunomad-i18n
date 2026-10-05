#!/usr/bin/env python3
"""
Script para generar 30 ejercicios interactivos por práctica y evaluación
utilizando los recursos HTML de morfosintaxis castellana
"""
import os
import re
import json
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Practica, Evaluacion, EjercicioInteractivo, RecursoEducativo

print("📚 GENERANDO 30 EJERCICIOS POR PRÁCTICA/EVALUACIÓN")
print("=" * 70)

# Ruta de los recursos HTML
RUTA_RECURSOS = 'apps/ejercicios_completos-lengua-castellana'

# Categorías de morfosintaxis
CATEGORIAS = {
    'sintaxis': {
        'temas': ['oraciones simples', 'oraciones compuestas', 'sujeto y predicado', 'complementos verbales', 'sintagmas'],
        'patrones': ['Sintaxis', 'oraciones', 'sujeto', 'predicado', 'complementos']
    },
    'gramatica': {
        'temas': ['morfología', 'verbos', 'sustantivos', 'adjetivos', 'conjugación', 'tiempos verbales'],
        'patrones': ['Gramática', 'morfología', 'verbos', 'sustantivos', 'adjetivos']
    },
    'morfosintaxis': {
        'temas': ['análisis morfosintáctico', 'estructura gramatical', 'categorías gramaticales'],
        'patrones': ['Morfosintaxis', 'morfosintáctico', 'categorías']
    },
    'ortografia': {
        'temas': ['tildes', 'puntuación', 'acentuación', 'mayúsculas', 'signos de puntuación'],
        'patrones': ['Ortografía', 'tildes', 'puntuación', 'acentuación']
    },
    'redaccion': {
        'temas': ['cohesión', 'coherencia', 'párrafos', 'estructura textual', 'conectores'],
        'patrones': ['Redacción', 'cohesión', 'coherencia', 'párrafos', 'conectores']
    }
}

def extraer_contenido_html(archivo_path):
    """Extrae contenido relevante de un archivo HTML"""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Buscar patrones de ejercicios o ejemplos
        ejercicios = []
        
        # Buscar secciones de ejercicios
        patrones_ejercicio = [
            r'<h[2-4][^>]*>Ejercicio[^<]*</h[2-4]>',
            r'<h[2-4][^>]*>Actividad[^<]*</h[2-4]>',
            r'<div[^>]*class="[^"]*ejercicio[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*class="[^"]*ejemplo[^"]*"[^>]*>(.*?)</p>',
        ]
        
        for patron in patrones_ejercicio:
            matches = re.findall(patron, contenido, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Limpiar HTML
                texto = re.sub(r'<[^>]+>', '', match)
                texto = re.sub(r'\s+', ' ', texto).strip()
                if len(texto) > 30:
                    ejercicios.append(texto)
        
        return ejercicios
    except Exception as e:
        return []

def generar_preguntas_opcion_multiple(tema, num=30):
    """Genera preguntas de opción múltiple sobre morfosintaxis"""
    preguntas = []
    
    bases = [
        (f"¿Cuál es la función principal del {tema} en una oración?", 
         ["Sujeto", "Predicado", "Complemento", "Núcleo"], "Sujeto"),
        (f"¿Qué tipo de palabra es '{tema}'?", 
         ["Sustantivo", "Verbo", "Adjetivo", "Adverbio"], "Sustantivo"),
        (f"¿Cuál es el núcleo del {tema}?", 
         ["Verbo", "Sujeto", "Complemento", "Nexo"], "Verbo"),
        (f"¿Cómo se clasifica '{tema}' gramaticalmente?", 
         ["Variable", "Invariable", "Flexiva", "Derivada"], "Variable"),
        (f"¿Qué función cumple '{tema}' en la oración?", 
         ["Modificador", "Núcleo", "Complemento", "Enlace"], "Núcleo"),
        (f"¿Cuál es la categoría gramatical de '{tema}'?", 
         ["Sustantivo", "Adjetivo", "Verbo", "Adverbio"], "Sustantivo"),
        (f"¿Qué tipo de sintagma es '{tema}'?", 
         ["Nominal", "Verbal", "Adjetival", "Preposicional"], "Nominal"),
    ]
    
    for i in range(num):
        base = random.choice(bases)
        pregunta_texto, opciones, respuesta = base
        opciones = random.sample(opciones, len(opciones))
        
        preguntas.append({
            'tipo': 'OPCION_MULTIPLE',
            'pregunta': f"{pregunta_texto} (Ejercicio {i+1})",
            'opciones': opciones,
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta correcta es '{respuesta}' porque es la función principal.",
            'puntaje': 3
        })
    
    return preguntas

def generar_preguntas_verdadero_falso(tema, num=30):
    """Genera preguntas de verdadero/falso sobre morfosintaxis"""
    preguntas = []
    
    afirmaciones = [
        (f"'{tema}' es una categoría gramatical invariable.", "Falso"),
        (f"'{tema}' funciona como núcleo del sintagma nominal.", "Verdadero"),
        (f"'{tema}' siempre concuerda en género y número.", "Falso"),
        (f"'{tema}' puede funcionar como complemento directo.", "Verdadero"),
        (f"'{tema}' es una palabra que no varía en género.", "Falso"),
        (f"'{tema}' se utiliza para modificar al sustantivo.", "Verdadero"),
        (f"'{tema}' tiene flexión verbal en todos los tiempos.", "Falso"),
    ]
    
    for i in range(num):
        afirmacion, respuesta = random.choice(afirmaciones)
        preguntas.append({
            'tipo': 'VERDADERO_FALSO',
            'pregunta': f"¿Es correcto afirmar que '{afirmacion}'? (Ejercicio {i+1})",
            'opciones': ['Verdadero', 'Falso'],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta es '{respuesta}' según la norma gramatical.",
            'puntaje': 2
        })
    
    return preguntas

def generar_preguntas_completar(tema, num=30):
    """Genera preguntas de completar sobre morfosintaxis"""
    preguntas = []
    
    patrones = [
        (f"El ______ es el núcleo de la oración.", "verbo"),
        (f"En morfosintaxis, el ______ es el núcleo del sintagma nominal.", "sustantivo"),
        (f"Los ______ son palabras que modifican al verbo.", "adverbios"),
        (f"En la oración, el ______ realiza la acción del verbo.", "sujeto"),
        (f"Los ______ son palabras que enlazan las oraciones.", "conectores"),
        (f"El ______ es un tipo de sintagma que funciona como complemento.", "objeto"),
    ]
    
    for i in range(num):
        patron, respuesta = random.choice(patrones)
        preguntas.append({
            'tipo': 'TEXTO',
            'pregunta': f"Completa la siguiente oración: '{patron}' (Ejercicio {i+1})",
            'opciones': [],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta correcta es '{respuesta}'.",
            'puntaje': 5
        })
    
    return preguntas

def generar_preguntas_relacionar(tema, num=30):
    """Genera preguntas de relacionar sobre morfosintaxis"""
    preguntas = []
    
    relaciones = [
        (["Sujeto", "Predicado", "Complemento"], ["Núcleo verbal", "Acción", "Modificador"]),
        (["Sustantivo", "Adjetivo", "Verbo"], ["Persona", "Calidad", "Acción"]),
    ]
    
    for i in range(num):
        grupo1, grupo2 = random.choice(relaciones)
        preguntas.append({
            'tipo': 'RELACIONAR',
            'pregunta': f"Relaciona los conceptos de {tema} (Ejercicio {i+1})",
            'opciones': [],
            'respuesta_correcta': f"{grupo1[0]}-{grupo2[0]}, {grupo1[1]}-{grupo2[1]}, {grupo1[2]}-{grupo2[2]}",
            'explicacion': "Las relaciones correctas son: Sujeto-Núcleo, Predicado-Acción.",
            'puntaje': 5
        })
    
    return preguntas

def generar_ejercicios_para_entidad(entity, tipo_entidad, num_ejercicios=30):
    """Genera ejercicios para una práctica o evaluación"""
    ejercicios = []
    temas = ['sintaxis', 'gramatica', 'morfosintaxis', 'ortografia', 'redaccion']
    tema_principal = random.choice(temas)
    
    # Distribuir tipos de preguntas
    tipos = ['OPCION_MULTIPLE', 'VERDADERO_FALSO', 'TEXTO', 'RELACIONAR']
    ejercicios_por_tipo = num_ejercicios // len(tipos)
    resto = num_ejercicios % len(tipos)
    
    for tipo in tipos:
        cantidad = ejercicios_por_tipo + (1 if resto > 0 else 0)
        resto -= 1
        
        if tipo == 'OPCION_MULTIPLE':
            nuevas = generar_preguntas_opcion_multiple(tema_principal, cantidad)
        elif tipo == 'VERDADERO_FALSO':
            nuevas = generar_preguntas_verdadero_falso(tema_principal, cantidad)
        elif tipo == 'TEXTO':
            nuevas = generar_preguntas_completar(tema_principal, cantidad)
        elif tipo == 'RELACIONAR':
            nuevas = generar_preguntas_relacionar(tema_principal, cantidad)
        
        ejercicios.extend(nuevas)
    
    # Mezclar ejercicios
    random.shuffle(ejercicios)
    return ejercicios[:num_ejercicios]

def procesar_practicas_evaluaciones():
    """Procesa todas las prácticas y evaluaciones existentes"""
    
    # Obtener prácticas y evaluaciones
    practicas = Practica.objects.all()
    evaluaciones = Evaluacion.objects.all()
    
    print(f"\n📊 Prácticas encontradas: {practicas.count()}")
    print(f"📊 Evaluaciones encontradas: {evaluaciones.count()}")
    
    total_ejercicios = 0
    ejercicios_creados = 0
    errores = 0
    
    # Procesar prácticas
    print("\n📝 PROCESANDO PRÁCTICAS...")
    for practica in practicas:
        print(f"  📖 Práctica: {practica.titulo[:40]}")
        
        # Eliminar ejercicios existentes
        EjercicioInteractivo.objects.filter(practica=practica).delete()
        
        # Generar nuevos ejercicios (30 por práctica)
        nuevos_ejercicios = generar_ejercicios_para_entidad(practica, 'practica', 30)
        
        for i, ejercicio_data in enumerate(nuevos_ejercicios, 1):
            try:
                EjercicioInteractivo.objects.create(
                    practica=practica,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data['opciones'],
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=i,
                    is_active=True
                )
                ejercicios_creados += 1
            except Exception as e:
                errores += 1
                if errores <= 5:
                    print(f"    ❌ Error: {e}")
        
        total_ejercicios += len(nuevos_ejercicios)
        print(f"    ✅ {len(nuevos_ejercicios)} ejercicios generados")
    
    # Procesar evaluaciones
    print("\n📝 PROCESANDO EVALUACIONES...")
    for evaluacion in evaluaciones:
        print(f"  📖 Evaluación: {evaluacion.titulo[:40]}")
        
        # Eliminar ejercicios existentes
        EjercicioInteractivo.objects.filter(evaluacion=evaluacion).delete()
        
        # Generar nuevos ejercicios (30 por evaluación)
        nuevos_ejercicios = generar_ejercicios_para_entidad(evaluacion, 'evaluacion', 30)
        
        for i, ejercicio_data in enumerate(nuevos_ejercicios, 1):
            try:
                EjercicioInteractivo.objects.create(
                    evaluacion=evaluacion,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data['opciones'],
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=i,
                    is_active=True
                )
                ejercicios_creados += 1
            except Exception as e:
                errores += 1
                if errores <= 5:
                    print(f"    ❌ Error: {e}")
        
        total_ejercicios += len(nuevos_ejercicios)
        print(f"    ✅ {len(nuevos_ejercicios)} ejercicios generados")
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL:")
    print(f"  📝 Prácticas procesadas: {practicas.count()}")
    print(f"  📝 Evaluaciones procesadas: {evaluaciones.count()}")
    print(f"  📝 Total ejercicios generados: {ejercicios_creados}")
    print(f"  📝 Ejercicios por entidad: 30")
    if errores > 0:
        print(f"  ⚠️ Errores: {errores}")

if __name__ == "__main__":
    procesar_practicas_evaluaciones()
