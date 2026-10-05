"""
Utilidades para la gestión de certificaciones
"""
from django.utils import timezone
from datetime import timedelta
from .models import Certificacion, ProgresoCurso, Practica, Evaluacion

def verificar_certificacion(usuario, curso):
    """Verifica si un usuario ha completado los requisitos para certificarse"""
    
    # Verificar progreso del curso
    progreso, created = ProgresoCurso.objects.get_or_create(
        usuario=usuario,
        curso=curso
    )
    
    # Obtener total de prácticas y evaluaciones del curso
    total_practicas = Practica.objects.filter(curso=curso, is_active=True).count()
    total_evaluaciones = Evaluacion.objects.filter(curso=curso, is_active=True).count()
    
    # Calcular porcentaje de completado
    total_requeridos = total_practicas + total_evaluaciones
    if total_requeridos == 0:
        return False, "No hay prácticas o evaluaciones disponibles"
    
    completados = progreso.practicas_completadas + progreso.evaluaciones_completadas
    porcentaje = (completados / total_requeridos) * 100
    
    # Requisitos para certificación
    requisitos = {
        'min_practicas': 0.7,  # 70% de prácticas completadas
        'min_evaluaciones': 0.6,  # 60% de evaluaciones completadas
        'min_puntaje': 60.0,  # Puntaje mínimo 60%
        'min_porcentaje': 70.0,  # 70% total completado
    }
    
    # Verificar requisitos
    practicas_completadas_porcentaje = (progreso.practicas_completadas / total_practicas * 100) if total_practicas > 0 else 100
    evaluaciones_completadas_porcentaje = (progreso.evaluaciones_completadas / total_evaluaciones * 100) if total_evaluaciones > 0 else 100
    
    certificable = (
        practicas_completadas_porcentaje >= requisitos['min_practicas'] * 100 and
        evaluaciones_completadas_porcentaje >= requisitos['min_evaluaciones'] * 100 and
        progreso.puntaje_total >= requisitos['min_puntaje'] and
        porcentaje >= requisitos['min_porcentaje']
    )
    
    return certificable, porcentaje

def generar_certificacion(usuario, curso):
    """Genera una certificación para un usuario"""
    
    # Verificar si ya existe certificación
    certificacion, created = Certificacion.objects.get_or_create(
        usuario=usuario,
        curso=curso,
        defaults={
            'estado': 'COMPLETADO',
            'fecha_completado': timezone.now(),
            'fecha_vencimiento': timezone.now() + timedelta(days=365),
        }
    )
    
    if not created and certificacion.estado == 'COMPLETADO':
        return certificacion, False  # Ya estaba certificado
    
    if not created:
        # Actualizar certificación existente
        certificacion.estado = 'COMPLETADO'
        certificacion.fecha_completado = timezone.now()
        certificacion.fecha_vencimiento = timezone.now() + timedelta(days=365)
    
    # Actualizar datos
    progreso = ProgresoCurso.objects.get(usuario=usuario, curso=curso)
    certificacion.puntaje_obtenido = progreso.puntaje_total
    certificacion.porcentaje = (progreso.practicas_completadas + progreso.evaluaciones_completadas) / max(1, Practica.objects.filter(curso=curso).count() + Evaluacion.objects.filter(curso=curso).count()) * 100
    certificacion.save()
    
    return certificacion, True

def registrar_progreso(usuario, curso, tipo, puntaje=None):
    """Registra el progreso del usuario en un curso"""
    
    progreso, created = ProgresoCurso.objects.get_or_create(
        usuario=usuario,
        curso=curso
    )
    
    if tipo == 'practica':
        progreso.practicas_completadas += 1
    elif tipo == 'evaluacion':
        progreso.evaluaciones_completadas += 1
    
    if puntaje:
        progreso.puntaje_total += puntaje
    
    progreso.ultimo_acceso = timezone.now()
    progreso.save()
    
    # Verificar si ya puede certificarse
    certificable, porcentaje = verificar_certificacion(usuario, curso)
    
    if certificable:
        certificacion, nueva = generar_certificacion(usuario, curso)
        return {
            'progreso': progreso,
            'certificable': True,
            'certificacion': certificacion,
            'porcentaje': porcentaje,
            'nueva_certificacion': nueva
        }
    
    return {
        'progreso': progreso,
        'certificable': False,
        'porcentaje': porcentaje,
    }
