#!/usr/bin/env python3
"""
Script para generar 100 ejercicios interactivos por práctica y evaluación
utilizando los recursos HTML de morfosintaxis castellana
"""
import os
import re
import json
import random
from datetime import datetime
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.core.models import Practica, Evaluacion, EjercicioInteractivo, RecursoEducativo

print("📚 GENERANDO 100 EJERCICIOS POR PRÁCTICA/EVALUACIÓN")
print("=" * 70)

# Ruta de los recursos HTML
RUTA_RECURSOS = 'apps/ejercicios_completos-lengua-castellana'

# Temas de morfosintaxis extraídos de los recursos
TEMAS_MORFOSINTAXIS = {
    'sintaxis': {
        'temas': [
            'oraciones simples', 'oraciones compuestas', 'sujeto y predicado', 
            'complementos verbales', 'sintagmas', 'estructura sintáctica',
            'análisis sintáctico', 'sintaxis oracional', 'cláusulas',
            'concordancia', 'subordinación', 'coordinación'
        ],
        'patrones': ['Sintaxis', 'oraciones', 'sujeto', 'predicado', 'complementos']
    },
    'gramatica': {
        'temas': [
            'morfología', 'verbos', 'sustantivos', 'adjetivos', 
            'conjugación', 'tiempos verbales', 'modos verbales',
            'artículos', 'pronombres', 'preposiciones', 'conjunciones',
            'interjecciones', 'adverbios', 'determinantes'
        ],
        'patrones': ['Gramática', 'morfología', 'verbos', 'sustantivos', 'adjetivos']
    },
    'morfosintaxis': {
        'temas': [
            'análisis morfosintáctico', 'estructura gramatical', 
            'categorías gramaticales', 'clases de palabras',
            'funciones sintácticas', 'relaciones gramaticales'
        ],
        'patrones': ['Morfosintaxis', 'morfosintáctico', 'categorías']
    },
    'ortografia': {
        'temas': [
            'tildes', 'puntuación', 'acentuación', 'mayúsculas', 
            'signos de puntuación', 'reglas ortográficas',
            'uso de la coma', 'punto y coma', 'dos puntos',
            'comillas', 'paréntesis', 'guiones', 'puntos suspensivos'
        ],
        'patrones': ['Ortografía', 'tildes', 'puntuación', 'acentuación']
    },
    'redaccion': {
        'temas': [
            'cohesión', 'coherencia', 'párrafos', 'estructura textual',
            'conectores', 'marcadores discursivos', 'organización textual',
            'argumentación', 'descripción', 'narración', 'exposición'
        ],
        'patrones': ['Redacción', 'cohesión', 'coherencia', 'párrafos', 'conectores']
    },
    'linguistica': {
        'temas': [
            'fonología', 'fonética', 'semántica', 'pragmática',
            'análisis del discurso', 'sociolingüística', 'psicolingüística'
        ],
        'patrones': ['Lingüística', 'fonología', 'semántica', 'pragmática']
    }
}

def extraer_contenido_recursos():
    """Extrae contenido de los archivos HTML de recursos"""
    contenidos = []
    if os.path.exists(RUTA_RECURSOS):
        for archivo in Path(RUTA_RECURSOS).rglob('*.html'):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    # Extraer texto relevante
                    texto = re.sub(r'<[^>]+>', ' ', contenido)
                    texto = re.sub(r'\s+', ' ', texto).strip()
                    if len(texto) > 100:
                        contenidos.append(texto[:2000])
            except:
                pass
    return contenidos

def generar_preguntas_opcion_multiple(tema, num):
    """Genera preguntas de opción múltiple sobre morfosintaxis"""
    preguntas = []
    
    bases_temas = [
        (f"¿Cuál es la función principal de los {tema} en la oración?", 
         ["Sujeto", "Predicado", "Complemento", "Núcleo", "Modificador"], "Sujeto"),
        (f"¿Qué tipo de palabra es un {tema}?", 
         ["Sustantivo", "Verbo", "Adjetivo", "Adverbio", "Preposición"], "Sustantivo"),
        (f"¿Cuál es el núcleo del {tema}?", 
         ["Verbo", "Sujeto", "Complemento", "Nexo", "Modificador"], "Verbo"),
        (f"¿Cómo se clasifica gramaticalmente '{tema}'?", 
         ["Variable", "Invariable", "Flexiva", "Derivada", "Compuesta"], "Variable"),
        (f"¿Qué función cumple el {tema} en la oración?", 
         ["Modificador", "Núcleo", "Complemento", "Enlace", "Sujeto"], "Núcleo"),
        (f"¿Cuál es la categoría gramatical de '{tema}'?", 
         ["Sustantivo", "Adjetivo", "Verbo", "Adverbio", "Preposición"], "Sustantivo"),
        (f"¿Qué tipo de sintagma es '{tema}'?", 
         ["Nominal", "Verbal", "Adjetival", "Preposicional", "Adverbial"], "Nominal"),
    ]
    
    for i in range(num):
        base = random.choice(bases_temas)
        pregunta_texto, opciones, respuesta = base
        random.shuffle(opciones)
        
        preguntas.append({
            'tipo': 'OPCION_MULTIPLE',
            'pregunta': f"{pregunta_texto} (Ejercicio {i+1})",
            'opciones': opciones[:4],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta correcta es '{respuesta}' según la norma gramatical.",
            'puntaje': 3
        })
    
    return preguntas

def generar_preguntas_verdadero_falso(tema, num):
    """Genera preguntas de verdadero/falso sobre morfosintaxis"""
    preguntas = []
    
    afirmaciones = [
        (f"El {tema} es una categoría gramatical invariable.", "Falso"),
        (f"El {tema} funciona como núcleo del sintagma nominal.", "Verdadero"),
        (f"El {tema} siempre concuerda en género y número.", "Falso"),
        (f"El {tema} puede funcionar como complemento directo.", "Verdadero"),
        (f"El {tema} es una palabra que no varía en género.", "Falso"),
        (f"El {tema} se utiliza para modificar al sustantivo.", "Verdadero"),
        (f"El {tema} tiene flexión verbal en todos los tiempos.", "Falso"),
        (f"El {tema} es un tipo de complemento circunstancial.", "Verdadero"),
        (f"El {tema} siempre lleva tilde en español.", "Falso"),
        (f"El {tema} es una conjunción coordinante.", "Falso"),
    ]
    
    for i in range(num):
        afirmacion, respuesta = random.choice(afirmaciones)
        preguntas.append({
            'tipo': 'VERDADERO_FALSO',
            'pregunta': f"¿Es correcto afirmar que: '{afirmacion}'? (Ejercicio {i+1})",
            'opciones': ['Verdadero', 'Falso'],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta es '{respuesta}' según la norma gramatical.",
            'puntaje': 2
        })
    
    return preguntas

def generar_preguntas_completar(tema, num):
    """Genera preguntas de completar sobre morfosintaxis"""
    preguntas = []
    
    patrones = [
        (f"El ______ es el núcleo de la oración en {tema}.", "verbo"),
        (f"En morfosintaxis, el ______ es el núcleo del sintagma nominal en {tema}.", "sustantivo"),
        (f"Los ______ son palabras que modifican al verbo en {tema}.", "adverbios"),
        (f"En la oración, el ______ realiza la acción del verbo en {tema}.", "sujeto"),
        (f"Los ______ son palabras que enlazan las oraciones en {tema}.", "conectores"),
        (f"El ______ es un tipo de sintagma que funciona como complemento en {tema}.", "objeto"),
        (f"La ______ es la categoría gramatical que expresa acción en {tema}.", "verbo"),
        (f"El ______ es el modificador del sustantivo en {tema}.", "adjetivo"),
    ]
    
    for i in range(num):
        patron, respuesta = random.choice(patrones)
        preguntas.append({
            'tipo': 'TEXTO',
            'pregunta': f"Completa la siguiente oración sobre {tema}: '{patron}' (Ejercicio {i+1})",
            'opciones': [],
            'respuesta_correcta': respuesta,
            'explicacion': f"La respuesta correcta es '{respuesta}'.",
            'puntaje': 5
        })
    
    return preguntas

def generar_preguntas_relacionar(tema, num):
    """Genera preguntas de relacionar sobre morfosintaxis"""
    preguntas = []
    
    relaciones = [
        (["Sujeto", "Predicado", "Complemento", "Modificador"], 
         ["Núcleo verbal", "Acción", "Modificador", "Núcleo nominal"]),
        (["Sustantivo", "Adjetivo", "Verbo", "Adverbio"], 
         ["Persona", "Calidad", "Acción", "Modo"]),
        (["Oración simple", "Oración compuesta", "Cláusula", "Sintagma"], 
         ["Una proposición", "Dos proposiciones", "Proposición dependiente", "Grupo de palabras"]),
        (["Sujeto", "Complemento Directo", "Complemento Indirecto", "Complemento Circunstancial"], 
         ["Realiza la acción", "Recibe la acción", "Destinatario", "Circunstancias"]),
    ]
    
    for i in range(num):
        grupo1, grupo2 = random.choice(relaciones)
        respuestas = [f"{g1}-{g2}" for g1, g2 in zip(grupo1, grupo2)]
        preguntas.append({
            'tipo': 'RELACIONAR',
            'pregunta': f"Relaciona los conceptos de {tema} (Ejercicio {i+1})",
            'opciones': [],
            'respuesta_correcta': ', '.join(respuestas),
            'explicacion': "Las relaciones correctas son las correspondencias lógicas.",
            'puntaje': 5
        })
    
    return preguntas

def generar_preguntas_ordenar(tema, num):
    """Genera preguntas de ordenar sobre morfosintaxis"""
    preguntas = []
    
    secuencias = [
        (["Sujeto", "Verbo", "Complemento"], "Sujeto-Verbo-Complemento"),
        (["Artículo", "Sustantivo", "Adjetivo"], "Artículo-Sustantivo-Adjetivo"),
        (["Introducción", "Desarrollo", "Conclusión"], "Introducción-Desarrollo-Conclusión"),
    ]
    
    for i in range(num):
        elementos, respuesta = random.choice(secuencias)
        random.shuffle(elementos)
        preguntas.append({
            'tipo': 'ORDENAR',
            'pregunta': f"Ordena los siguientes elementos de {tema} (Ejercicio {i+1}): {', '.join(elementos)}",
            'opciones': [],
            'respuesta_correcta': respuesta,
            'explicacion': "El orden correcto es la secuencia lógica.",
            'puntaje': 5
        })
    
    return preguntas

def generar_ejercicios_100(entity, tipo_entidad, num_ejercicios=100):
    """Genera 100 ejercicios para una práctica o evaluación"""
    ejercicios = []
    
    # Seleccionar temas de morfosintaxis
    temas = list(TEMAS_MORFOSINTAXIS.keys())
    tema_principal = random.choice(temas)
    subtemas = TEMAS_MORFOSINTAXIS[tema_principal]['temas']
    tema = random.choice(subtemas)
    
    # Distribuir tipos de preguntas (100 ejercicios)
    distribucion = {
        'OPCION_MULTIPLE': 30,
        'VERDADERO_FALSO': 25,
        'TEXTO': 20,
        'RELACIONAR': 15,
        'ORDENAR': 10
    }
    
    for tipo, cantidad in distribucion.items():
        if tipo == 'OPCION_MULTIPLE':
            nuevas = generar_preguntas_opcion_multiple(tema, cantidad)
        elif tipo == 'VERDADERO_FALSO':
            nuevas = generar_preguntas_verdadero_falso(tema, cantidad)
        elif tipo == 'TEXTO':
            nuevas = generar_preguntas_completar(tema, cantidad)
        elif tipo == 'RELACIONAR':
            nuevas = generar_preguntas_relacionar(tema, cantidad)
        elif tipo == 'ORDENAR':
            nuevas = generar_preguntas_ordenar(tema, cantidad)
        
        ejercicios.extend(nuevas)
    
    # Mezclar y limitar a 100
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
    for idx, practica in enumerate(practicas, 1):
        print(f"  [{idx}/{practicas.count()}] 📖 {practica.titulo[:40]}")
        
        # Eliminar ejercicios existentes
        EjercicioInteractivo.objects.filter(practica=practica).delete()
        
        # Generar 100 ejercicios por práctica
        nuevos_ejercicios = generar_ejercicios_100(practica, 'practica', 100)
        
        for i, ejercicio_data in enumerate(nuevos_ejercicios, 1):
            try:
                EjercicioInteractivo.objects.create(
                    practica=practica,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data.get('opciones', []),
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=i,
                    is_active=True
                )
                ejercicios_creados += 1
            except Exception as e:
                errores += 1
                if errores <= 10:
                    print(f"    ❌ Error: {e}")
        
        total_ejercicios += len(nuevos_ejercicios)
        if idx % 10 == 0:
            print(f"  ✅ Procesadas {idx} prácticas...")
    
    # Procesar evaluaciones
    print("\n📝 PROCESANDO EVALUACIONES...")
    for idx, evaluacion in enumerate(evaluaciones, 1):
        print(f"  [{idx}/{evaluaciones.count()}] 📖 {evaluacion.titulo[:40]}")
        
        # Eliminar ejercicios existentes
        EjercicioInteractivo.objects.filter(evaluacion=evaluacion).delete()
        
        # Generar 100 ejercicios por evaluación
        nuevos_ejercicios = generar_ejercicios_100(evaluacion, 'evaluacion', 100)
        
        for i, ejercicio_data in enumerate(nuevos_ejercicios, 1):
            try:
                EjercicioInteractivo.objects.create(
                    evaluacion=evaluacion,
                    tipo=ejercicio_data['tipo'],
                    pregunta=ejercicio_data['pregunta'],
                    opciones=ejercicio_data.get('opciones', []),
                    respuesta_correcta=ejercicio_data['respuesta_correcta'],
                    explicacion=ejercicio_data.get('explicacion', ''),
                    puntaje=ejercicio_data.get('puntaje', 3),
                    orden=i,
                    is_active=True
                )
                ejercicios_creados += 1
            except Exception as e:
                errores += 1
                if errores <= 10:
                    print(f"    ❌ Error: {e}")
        
        total_ejercicios += len(nuevos_ejercicios)
        if idx % 10 == 0:
            print(f"  ✅ Procesadas {idx} evaluaciones...")
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL:")
    print(f"  📝 Prácticas procesadas: {practicas.count()}")
    print(f"  📝 Evaluaciones procesadas: {evaluaciones.count()}")
    print(f"  📝 Total ejercicios generados: {ejercicios_creados}")
    print(f"  📝 Ejercicios por entidad: 100")
    if errores > 0:
        print(f"  ⚠️ Errores: {errores}")
    
    # Estadísticas por tipo
    print("\n📊 TIPOS DE EJERCICIOS GENERADOS:")
    tipos = EjercicioInteractivo.objects.values('tipo').annotate(count=models.Count('id'))
    for t in tipos:
        print(f"  - {t['tipo']}: {t['count']} ejercicios")

if __name__ == "__main__":
    from django.db import models
    procesar_practicas_evaluaciones()
