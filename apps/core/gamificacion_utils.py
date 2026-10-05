"""
Utilidades para el sistema de gamificación
"""
from django.utils import timezone
from datetime import timedelta
from .models import Insignia, InsigniaUsuario, PuntajeUsuario, Certificacion, ProgresoCurso

def inicializar_insignias():
    """Inicializa las insignias predefinidas"""
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
            defaults=data
        )
        if created:
            creadas += 1
    return creadas

def obtener_puntaje_usuario(usuario):
    """Obtiene o crea el puntaje del usuario"""
    puntaje, created = PuntajeUsuario.objects.get_or_create(usuario=usuario)
    return puntaje

def actualizar_puntaje(usuario, puntos, tipo_ejercicio='ejercicio'):
    """Actualiza el puntaje del usuario y verifica insignias"""
    puntaje = obtener_puntaje_usuario(usuario)
    
    # Actualizar puntos
    puntaje.puntos_totales += puntos
    puntaje.ejercicios_resueltos += 1
    if tipo_ejercicio == 'correcto':
        puntaje.ejercicios_correctos += 1
    
    # Actualizar racha
    if puntaje.ultimo_ejercicio:
        if (timezone.now() - puntaje.ultimo_ejercicio) < timedelta(days=1):
            puntaje.racha_actual += 1
            if puntaje.racha_actual > puntaje.racha_maxima:
                puntaje.racha_maxima = puntaje.racha_actual
        else:
            puntaje.racha_actual = 1
    else:
        puntaje.racha_actual = 1
    
    puntaje.ultimo_ejercicio = timezone.now()
    puntaje.save()
    
    # Verificar insignias
    verificar_insignias(usuario)
    
    return puntaje

def verificar_insignias(usuario):
    """Verifica si el usuario merece nuevas insignias"""
    puntaje = obtener_puntaje_usuario(usuario)
    
    # Contar prácticas completadas
    practicas_completadas = ProgresoCurso.objects.filter(
        usuario=usuario,
        completado=True
    ).count()
    
    # Contar certificaciones
    certificaciones = Certificacion.objects.filter(
        usuario=usuario,
        estado='COMPLETADO'
    ).count()
    
    # Verificar cada insignia
    for insignia in Insignia.objects.filter(is_active=True):
        # Verificar si ya la tiene
        if InsigniaUsuario.objects.filter(usuario=usuario, insignia=insignia).exists():
            continue
        
        # Verificar requisitos según tipo
        requisito_cumplido = False
        
        if insignia.tipo == 'PRACTICA':
            if insignia.nombre == 'Primer Paso' and practicas_completadas >= 1:
                requisito_cumplido = True
            elif insignia.nombre == 'Estudiante Constante' and practicas_completadas >= 5:
                requisito_cumplido = True
            elif insignia.nombre == 'Experto en Prácticas' and practicas_completadas >= 10:
                requisito_cumplido = True
                
        elif insignia.tipo == 'EVALUACION':
            if insignia.nombre == 'Primera Evaluación' and practicas_completadas >= 1:
                requisito_cumplido = True
                
        elif insignia.tipo == 'CURSO':
            if insignia.nombre == 'Curso Completado' and practicas_completadas >= 1:
                requisito_cumplido = True
                
        elif insignia.tipo == 'CERTIFICACION':
            if insignia.nombre == 'Maestro Certificado' and certificaciones >= 1:
                requisito_cumplido = True
                
        elif insignia.tipo == 'RACHA':
            if insignia.nombre == 'Racha de Oro' and puntaje.racha_maxima >= 7:
                requisito_cumplido = True
        
        # Asignar insignia si cumple requisitos
        if requisito_cumplido:
            InsigniaUsuario.objects.create(
                usuario=usuario,
                insignia=insignia,
                progreso=100.0
            )

def obtener_estadisticas_usuario(usuario):
    """Obtiene estadísticas completas del usuario"""
    puntaje = obtener_puntaje_usuario(usuario)
    insignias = InsigniaUsuario.objects.filter(usuario=usuario).select_related('insignia')
    certificaciones = Certificacion.objects.filter(usuario=usuario, estado='COMPLETADO')
    
    # Calcular nivel
    niveles = ['BRONCE', 'PLATA', 'ORO', 'DIAMANTE', 'EXPERTO']
    puntos_por_nivel = [0, 100, 500, 1000, 2000]
    nivel_actual = 'BRONCE'
    for i, nivel in enumerate(niveles):
        if puntaje.puntos_totales >= puntos_por_nivel[i]:
            nivel_actual = nivel
    
    # Agrupar insignias por tipo
    insignias_por_tipo = {}
    for ins in insignias:
        tipo = ins.insignia.tipo
        if tipo not in insignias_por_tipo:
            insignias_por_tipo[tipo] = []
        insignias_por_tipo[tipo].append(ins)
    
    return {
        'puntaje': puntaje,
        'nivel': nivel_actual,
        'insignias': insignias,
        'total_insignias': insignias.count(),
        'insignias_por_tipo': insignias_por_tipo,
        'certificaciones': certificaciones.count(),
        'racha_actual': puntaje.racha_actual,
        'racha_maxima': puntaje.racha_maxima,
        'precision': puntaje.porcentaje_precision,
        'puntos_totales': puntaje.puntos_totales,
    }
