from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import RecursoEducativo, Curso
from .serializers import (
    RecursoEducativoSerializer, RecursoEducativoSimpleSerializer,
    CursoSerializer, CursoSimpleSerializer
)

def home(request):
    """Vista principal - Dashboard"""
    recursos = RecursoEducativo.objects.all()
    cursos = Curso.objects.all().order_by('-id')[:10]
    
    total_recursos = recursos.count()
    total_cursos = cursos.count()
    total_categorias = recursos.values('categoria').distinct().count()
    total_bytes = recursos.aggregate(Sum('tamanio_bytes'))['tamanio_bytes__sum'] or 0
    total_mb = round(total_bytes / (1024 * 1024), 1)
    
    context = {
        'total_recursos': total_recursos,
        'total_cursos': total_cursos,
        'total_categorias': total_categorias,
        'total_mb': total_mb,
        'cursos': cursos,
        'recursos': recursos,
    }
    return render(request, 'lms/home.html', context)

def explorar_recursos(request):
    """Vista para explorar recursos educativos"""
    recursos = RecursoEducativo.objects.all().order_by('-id')
    categorias = RecursoEducativo.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'recursos': recursos,
        'categorias': categorias,
        'total_recursos': recursos.count(),
    }
    return render(request, 'lms/explorar_recursos.html', context)

def lista_cursos(request):
    """Vista para listar todos los cursos"""
    cursos = Curso.objects.all().order_by('-fecha_creacion')
    
    # Calcular total de recursos por curso (usando annotate)
    cursos = cursos.annotate(total_recursos_count=Count('recursos'))
    
    context = {
        'cursos': cursos,
        'total_cursos': cursos.count(),
    }
    return render(request, 'lms/cursos/lista.html', context)

def detalle_curso(request, curso_id):
    """Vista para ver detalle de un curso"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Obtener recursos del curso
    recursos = curso.recursos.all()
    
    # Intentar obtener lecciones (desde language_practice)
    try:
        from apps.language_practice.models import Course, Lesson
        course_lp = Course.objects.filter(title=curso.titulo).first()
        lecciones = Lesson.objects.filter(course=course_lp).order_by('order') if course_lp else []
    except:
        lecciones = []
    
    context = {
        'curso': curso,
        'recursos': recursos,
        'lecciones': lecciones,
        'total_recursos': recursos.count(),
        'total_lecciones': len(lecciones),
    }
    return render(request, 'lms/cursos/detalle.html', context)


# API Views
class RecursoEducativoViewSet(viewsets.ModelViewSet):
    queryset = RecursoEducativo.objects.all()
    serializer_class = RecursoEducativoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_archivo', 'categoria', 'descripcion', 'etiquetas']
    ordering_fields = ['nombre_archivo', 'categoria', 'tamanio_bytes', 'fecha_creacion']
    ordering = ['categoria', 'nombre_archivo']
    
    @action(detail=False, methods=['get'])
    def categorias(self, request):
        categorias = RecursoEducativo.objects.values('categoria').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
        
        total = RecursoEducativo.objects.count()
        for cat in categorias:
            cat['porcentaje'] = round(cat['cantidad'] / total * 100, 1) if total > 0 else 0
        
        return Response(categorias)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        total = RecursoEducativo.objects.count()
        total_bytes = RecursoEducativo.objects.aggregate(
            total_bytes=Sum('tamanio_bytes')
        )['total_bytes'] or 0
        
        categorias = RecursoEducativo.objects.values('categoria').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
        
        return Response({
            'total_archivos': total,
            'total_mb': round(total_bytes / (1024 * 1024), 2),
            'categorias': categorias,
        })


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descripcion', 'categoria', 'palabras_clave']
    ordering_fields = ['titulo', 'categoria', 'nivel', 'duracion_horas', 'precio', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        total = Curso.objects.count()
        publicados = Curso.objects.filter(estado='PUBLICADO').count()
        
        return Response({
            'total_cursos': total,
            'cursos_publicados': publicados,
        })

def detalle_practica(request, practica_id):
    """Vista para ver una práctica interactiva"""
    from .models import Practica, EjercicioInteractivo
    
    practica = get_object_or_404(Practica, id=practica_id, is_active=True)
    ejercicios = EjercicioInteractivo.objects.filter(practica=practica, is_active=True).order_by('orden')
    
    context = {
        'practica': practica,
        'ejercicios': ejercicios,
        'total_ejercicios': ejercicios.count(),
    }
    return render(request, 'lms/practicas/detalle.html', context)

def detalle_evaluacion(request, evaluacion_id):
    """Vista para ver una evaluación"""
    from .models import Evaluacion, EjercicioInteractivo
    
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, is_active=True)
    ejercicios = EjercicioInteractivo.objects.filter(evaluacion=evaluacion, is_active=True).order_by('orden')
    
    context = {
        'evaluacion': evaluacion,
        'ejercicios': ejercicios,
        'total_ejercicios': ejercicios.count(),
    }
    return render(request, 'lms/evaluaciones/detalle.html', context)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Practica, Evaluacion, EjercicioInteractivo
from .certificacion_utils import registrar_progreso, verificar_certificacion, generar_certificacion

@login_required
def enviar_practica(request, practica_id):
    """Vista para enviar una práctica y registrar progreso"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    practica = get_object_or_404(Practica, id=practica_id, is_active=True)
    usuario = request.user
    
    # Obtener respuestas del usuario
    respuestas = request.POST.get('respuestas', '{}')
    import json
    try:
        respuestas = json.loads(respuestas)
    except:
        respuestas = {}
    
    # Calcular puntaje
    ejercicios = EjercicioInteractivo.objects.filter(practica=practica, is_active=True)
    puntaje_total = 0
    respuestas_correctas = 0
    
    for ejercicio in ejercicios:
        respuesta_usuario = respuestas.get(str(ejercicio.id), '')
        if respuesta_usuario and respuesta_usuario == ejercicio.respuesta_correcta:
            puntaje_total += ejercicio.puntaje
            respuestas_correctas += 1
    
    # Registrar progreso
    resultado = registrar_progreso(
        usuario=usuario,
        curso=practica.curso,
        tipo='practica',
        puntaje=puntaje_total
    )
    
    return JsonResponse({
        'success': True,
        'puntaje': puntaje_total,
        'respuestas_correctas': respuestas_correctas,
        'total_ejercicios': ejercicios.count(),
        'certificable': resultado['certificable'],
        'porcentaje': resultado.get('porcentaje', 0),
        'certificacion_generada': resultado.get('nueva_certificacion', False)
    })

@login_required
def enviar_evaluacion(request, evaluacion_id):
    """Vista para enviar una evaluación y registrar progreso"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, is_active=True)
    usuario = request.user
    
    # Obtener respuestas del usuario
    respuestas = request.POST.get('respuestas', '{}')
    import json
    try:
        respuestas = json.loads(respuestas)
    except:
        respuestas = {}
    
    # Calcular puntaje
    ejercicios = EjercicioInteractivo.objects.filter(evaluacion=evaluacion, is_active=True)
    puntaje_total = 0
    respuestas_correctas = 0
    
    for ejercicio in ejercicios:
        respuesta_usuario = respuestas.get(str(ejercicio.id), '')
        if respuesta_usuario and respuesta_usuario == ejercicio.respuesta_correcta:
            puntaje_total += ejercicio.puntaje
            respuestas_correctas += 1
    
    # Registrar progreso
    resultado = registrar_progreso(
        usuario=usuario,
        curso=evaluacion.curso,
        tipo='evaluacion',
        puntaje=puntaje_total
    )
    
    return JsonResponse({
        'success': True,
        'puntaje': puntaje_total,
        'respuestas_correctas': respuestas_correctas,
        'total_ejercicios': ejercicios.count(),
        'certificable': resultado['certificable'],
        'porcentaje': resultado.get('porcentaje', 0),
        'certificacion_generada': resultado.get('nueva_certificacion', False)
    })

@login_required
def mis_certificaciones(request):
    """Vista para ver las certificaciones del usuario"""
    certificaciones = Certificacion.objects.filter(
        usuario=request.user,
        estado='COMPLETADO'
    ).order_by('-fecha_completado')
    
    context = {
        'certificaciones': certificaciones,
        'total': certificaciones.count(),
    }
    return render(request, 'lms/certificaciones/lista.html', context)

@login_required
def ver_certificacion(request, certificacion_id):
    """Vista para ver una certificación específica"""
    certificacion = get_object_or_404(Certificacion, id=certificacion_id, usuario=request.user)
    return render(request, 'lms/certificaciones/detalle.html', {'certificacion': certificacion})

@login_required
def progreso_curso(request, curso_id):
    """Vista para ver el progreso en un curso"""
    curso = get_object_or_404(Curso, id=curso_id)
    progreso, created = ProgresoCurso.objects.get_or_create(
        usuario=request.user,
        curso=curso
    )
    
    total_practicas = Practica.objects.filter(curso=curso, is_active=True).count()
    total_evaluaciones = Evaluacion.objects.filter(curso=curso, is_active=True).count()
    
    context = {
        'curso': curso,
        'progreso': progreso,
        'total_practicas': total_practicas,
        'total_evaluaciones': total_evaluaciones,
    }
    return render(request, 'lms/cursos/progreso.html', context)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Practica, Evaluacion, EjercicioInteractivo, Certificacion, ProgresoCurso
from .certificacion_utils import registrar_progreso, verificar_certificacion, generar_certificacion

@login_required
def enviar_practica(request, practica_id):
    """Vista para enviar una práctica y registrar progreso"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    practica = get_object_or_404(Practica, id=practica_id, is_active=True)
    usuario = request.user
    
    # Obtener respuestas del usuario
    import json
    respuestas = json.loads(request.POST.get('respuestas', '{}'))
    
    # Calcular puntaje
    ejercicios = EjercicioInteractivo.objects.filter(practica=practica, is_active=True)
    puntaje_total = 0
    respuestas_correctas = 0
    
    for ejercicio in ejercicios:
        respuesta_usuario = respuestas.get(str(ejercicio.id), '')
        if respuesta_usuario and respuesta_usuario == ejercicio.respuesta_correcta:
            puntaje_total += ejercicio.puntaje
            respuestas_correctas += 1
    
    # Registrar progreso
    resultado = registrar_progreso(
        usuario=usuario,
        curso=practica.curso,
        tipo='practica',
        puntaje=puntaje_total
    )
    
    return JsonResponse({
        'success': True,
        'puntaje': puntaje_total,
        'respuestas_correctas': respuestas_correctas,
        'total_ejercicios': ejercicios.count(),
        'certificable': resultado.get('certificable', False),
        'porcentaje': resultado.get('porcentaje', 0),
        'certificacion_generada': resultado.get('nueva_certificacion', False)
    })

@login_required
def enviar_evaluacion(request, evaluacion_id):
    """Vista para enviar una evaluación y registrar progreso"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, is_active=True)
    usuario = request.user
    
    # Obtener respuestas del usuario
    import json
    respuestas = json.loads(request.POST.get('respuestas', '{}'))
    
    # Calcular puntaje
    ejercicios = EjercicioInteractivo.objects.filter(evaluacion=evaluacion, is_active=True)
    puntaje_total = 0
    respuestas_correctas = 0
    
    for ejercicio in ejercicios:
        respuesta_usuario = respuestas.get(str(ejercicio.id), '')
        if respuesta_usuario and respuesta_usuario == ejercicio.respuesta_correcta:
            puntaje_total += ejercicio.puntaje
            respuestas_correctas += 1
    
    # Registrar progreso
    resultado = registrar_progreso(
        usuario=usuario,
        curso=evaluacion.curso,
        tipo='evaluacion',
        puntaje=puntaje_total
    )
    
    return JsonResponse({
        'success': True,
        'puntaje': puntaje_total,
        'respuestas_correctas': respuestas_correctas,
        'total_ejercicios': ejercicios.count(),
        'certificable': resultado.get('certificable', False),
        'porcentaje': resultado.get('porcentaje', 0),
        'certificacion_generada': resultado.get('nueva_certificacion', False)
    })

@login_required
def mis_certificaciones(request):
    """Vista para ver las certificaciones del usuario"""
    certificaciones = Certificacion.objects.filter(
        usuario=request.user,
        estado='COMPLETADO'
    ).order_by('-fecha_completado')
    
    context = {
        'certificaciones': certificaciones,
        'total': certificaciones.count(),
    }
    return render(request, 'lms/certificaciones/lista.html', context)

@login_required
def ver_certificacion(request, certificacion_id):
    """Vista para ver una certificación específica"""
    certificacion = get_object_or_404(Certificacion, id=certificacion_id, usuario=request.user)
    return render(request, 'lms/certificaciones/detalle.html', {'certificacion': certificacion})

@login_required
def progreso_curso(request, curso_id):
    """Vista para ver el progreso en un curso"""
    curso = get_object_or_404(Curso, id=curso_id)
    progreso, created = ProgresoCurso.objects.get_or_create(
        usuario=request.user,
        curso=curso
    )
    
    total_practicas = Practica.objects.filter(curso=curso, is_active=True).count()
    total_evaluaciones = Evaluacion.objects.filter(curso=curso, is_active=True).count()
    
    context = {
        'curso': curso,
        'progreso': progreso,
        'total_practicas': total_practicas,
        'total_evaluaciones': total_evaluaciones,
    }
    return render(request, 'lms/cursos/progreso.html', context)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import EntregaArchivo, ComentarioEntrega
import os
import mimetypes

@login_required
def subir_archivo(request):
    """Vista para subir archivo adjunto a práctica/evaluación"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    practica_id = request.POST.get('practica_id')
    evaluacion_id = request.POST.get('evaluacion_id')
    titulo = request.POST.get('titulo', 'Sin título')
    descripcion = request.POST.get('descripcion', '')
    
    if not practica_id and not evaluacion_id:
        return JsonResponse({'error': 'Se requiere práctica o evaluación'}, status=400)
    
    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se ha seleccionado ningún archivo'}, status=400)
    
    archivo = request.FILES['archivo']
    
    # Validar tamaño (máximo 50MB)
    if archivo.size > 50 * 1024 * 1024:
        return JsonResponse({'error': 'El archivo no puede superar los 50MB'}, status=400)
    
    # Validar extensión
    extensiones_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', 
                             '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.txt', '.zip', '.rar']
    extension = os.path.splitext(archivo.name)[1].lower()
    if extension and extension not in extensiones_permitidas:
        return JsonResponse({'error': f'Extensión {extension} no permitida'}, status=400)
    
    # Determinar tipo
    tipos = {
        '.mp3': 'AUDIO', '.wav': 'AUDIO', '.ogg': 'AUDIO', '.m4a': 'AUDIO',
        '.jpg': 'IMAGEN', '.jpeg': 'IMAGEN', '.png': 'IMAGEN', '.gif': 'IMAGEN', '.svg': 'IMAGEN', '.webp': 'IMAGEN',
        '.pdf': 'PDF',
        '.mp4': 'VIDEO', '.avi': 'VIDEO', '.mov': 'VIDEO', '.wmv': 'VIDEO', '.flv': 'VIDEO',
        '.doc': 'DOCUMENTO', '.docx': 'DOCUMENTO', '.txt': 'DOCUMENTO', '.zip': 'DOCUMENTO', '.rar': 'DOCUMENTO'
    }
    tipo_archivo = tipos.get(extension, 'OTRO')
    
    # Crear entrega
    entrega = EntregaArchivo.objects.create(
        usuario=request.user,
        practica_id=practica_id if practica_id else None,
        evaluacion_id=evaluacion_id if evaluacion_id else None,
        titulo=titulo[:200],
        descripcion=descripcion,
        tipo_archivo=tipo_archivo,
        nombre_original=archivo.name[:255],
        tamanio_bytes=archivo.size,
        extension=extension,
        ip_origen=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
    )
    
    # Guardar archivo
    path = default_storage.save(f'entregas/{entrega.id}/{archivo.name}', ContentFile(archivo.read()))
    entrega.archivo = path
    entrega.save()
    
    return JsonResponse({
        'success': True,
        'entrega_id': entrega.id,
        'titulo': entrega.titulo,
        'mensaje': f'Archivo {archivo.name} subido correctamente'
    })

@login_required
def listar_entregas(request):
    """Vista para listar entregas del usuario"""
    practica_id = request.GET.get('practica_id')
    evaluacion_id = request.GET.get('evaluacion_id')
    
    entregas = EntregaArchivo.objects.filter(usuario=request.user)
    
    if practica_id:
        entregas = entregas.filter(practica_id=practica_id)
    if evaluacion_id:
        entregas = entregas.filter(evaluacion_id=evaluacion_id)
    
    entregas = entregas.order_by('-fecha_entrega')
    
    data = []
    for e in entregas:
        data.append({
            'id': e.id,
            'titulo': e.titulo,
            'tipo': e.tipo_archivo,
            'extension': e.extension,
            'tamanio_mb': e.tamanio_mb,
            'estado': e.estado,
            'fecha': e.fecha_entrega.strftime('%Y-%m-%d %H:%M'),
            'url': e.archivo.url if e.archivo else None,
        })
    
    return JsonResponse(data, safe=False)

@login_required
def descargar_entrega(request, entrega_id):
    """Vista para descargar un archivo de entrega"""
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id)
    
    # Verificar permiso (usuario o profesor)
    if request.user != entrega.usuario and not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permiso'}, status=403)
    
    if not entrega.archivo or not default_storage.exists(entrega.archivo):
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)
    
    # Abrir archivo
    file_content = default_storage.open(entrega.archivo).read()
    response = HttpResponse(file_content, content_type=mimetypes.guess_type(entrega.nombre_original)[0] or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{entrega.nombre_original}"'
    return response

@login_required
def eliminar_entrega(request, entrega_id):
    """Vista para eliminar una entrega"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id, usuario=request.user)
    
    # Eliminar archivo físico
    if entrega.archivo and default_storage.exists(entrega.archivo):
        default_storage.delete(entrega.archivo)
    
    entrega.delete()
    return JsonResponse({'success': True, 'mensaje': 'Entrega eliminada correctamente'})

@login_required
def detalle_entrega(request, entrega_id):
    """Vista para ver detalle de una entrega"""
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id, usuario=request.user)
    
    context = {
        'entrega': entrega,
        'comentarios': entrega.comentarios.all().order_by('fecha'),
    }
    return render(request, 'lms/entregas/detalle.html', context)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import EntregaArchivo, ComentarioEntrega
import os
import mimetypes
import json

@login_required
def subir_archivo(request):
    """Vista para subir archivo adjunto a práctica/evaluación"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    practica_id = request.POST.get('practica_id')
    evaluacion_id = request.POST.get('evaluacion_id')
    titulo = request.POST.get('titulo', 'Sin título')
    descripcion = request.POST.get('descripcion', '')
    
    if not practica_id and not evaluacion_id:
        return JsonResponse({'error': 'Se requiere práctica o evaluación'}, status=400)
    
    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se ha seleccionado ningún archivo'}, status=400)
    
    archivo = request.FILES['archivo']
    
    # Validar tamaño (máximo 50MB)
    if archivo.size > 50 * 1024 * 1024:
        return JsonResponse({'error': 'El archivo no puede superar los 50MB'}, status=400)
    
    # Validar extensión
    extensiones_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', 
                             '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.txt', '.zip', '.rar']
    extension = os.path.splitext(archivo.name)[1].lower()
    if extension and extension not in extensiones_permitidas:
        return JsonResponse({'error': f'Extensión {extension} no permitida'}, status=400)
    
    # Determinar tipo
    tipos = {
        '.mp3': 'AUDIO', '.wav': 'AUDIO', '.ogg': 'AUDIO', '.m4a': 'AUDIO',
        '.jpg': 'IMAGEN', '.jpeg': 'IMAGEN', '.png': 'IMAGEN', '.gif': 'IMAGEN', '.svg': 'IMAGEN', '.webp': 'IMAGEN',
        '.pdf': 'PDF',
        '.mp4': 'VIDEO', '.avi': 'VIDEO', '.mov': 'VIDEO', '.wmv': 'VIDEO', '.flv': 'VIDEO',
        '.doc': 'DOCUMENTO', '.docx': 'DOCUMENTO', '.txt': 'DOCUMENTO', '.zip': 'DOCUMENTO', '.rar': 'DOCUMENTO'
    }
    tipo_archivo = tipos.get(extension, 'OTRO')
    
    # Crear entrega
    entrega = EntregaArchivo.objects.create(
        usuario=request.user,
        practica_id=practica_id if practica_id else None,
        evaluacion_id=evaluacion_id if evaluacion_id else None,
        titulo=titulo[:200],
        descripcion=descripcion,
        tipo_archivo=tipo_archivo,
        nombre_original=archivo.name[:255],
        tamanio_bytes=archivo.size,
        extension=extension,
        ip_origen=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
    )
    
    # Guardar archivo
    path = default_storage.save(f'entregas/{entrega.id}/{archivo.name}', ContentFile(archivo.read()))
    entrega.archivo = path
    entrega.save()
    
    return JsonResponse({
        'success': True,
        'entrega_id': entrega.id,
        'titulo': entrega.titulo,
        'mensaje': f'Archivo {archivo.name} subido correctamente'
    })

@login_required
def listar_entregas(request):
    """Vista para listar entregas del usuario"""
    practica_id = request.GET.get('practica_id')
    evaluacion_id = request.GET.get('evaluacion_id')
    
    entregas = EntregaArchivo.objects.filter(usuario=request.user)
    
    if practica_id:
        entregas = entregas.filter(practica_id=practica_id)
    if evaluacion_id:
        entregas = entregas.filter(evaluacion_id=evaluacion_id)
    
    entregas = entregas.order_by('-fecha_entrega')
    
    data = []
    for e in entregas:
        data.append({
            'id': e.id,
            'titulo': e.titulo,
            'tipo': e.tipo_archivo,
            'extension': e.extension,
            'tamanio_mb': e.tamanio_mb,
            'estado': e.estado,
            'fecha': e.fecha_entrega.strftime('%Y-%m-%d %H:%M'),
            'url': e.archivo.url if e.archivo else None,
        })
    
    return JsonResponse(data, safe=False)

@login_required
def descargar_entrega(request, entrega_id):
    """Vista para descargar un archivo de entrega"""
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id)
    
    # Verificar permiso (usuario o profesor)
    if request.user != entrega.usuario and not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permiso'}, status=403)
    
    if not entrega.archivo or not default_storage.exists(entrega.archivo):
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)
    
    # Abrir archivo
    file_content = default_storage.open(entrega.archivo).read()
    content_type = mimetypes.guess_type(entrega.nombre_original)[0] or 'application/octet-stream'
    response = HttpResponse(file_content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{entrega.nombre_original}"'
    return response

@login_required
def eliminar_entrega(request, entrega_id):
    """Vista para eliminar una entrega"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id, usuario=request.user)
    
    # Eliminar archivo físico
    if entrega.archivo and default_storage.exists(entrega.archivo):
        default_storage.delete(entrega.archivo)
    
    entrega.delete()
    return JsonResponse({'success': True, 'mensaje': 'Entrega eliminada correctamente'})

@login_required
def detalle_entrega(request, entrega_id):
    """Vista para ver detalle de una entrega"""
    entrega = get_object_or_404(EntregaArchivo, id=entrega_id, usuario=request.user)
    
    context = {
        'entrega': entrega,
        'comentarios': entrega.comentarios.all().order_by('fecha'),
    }
    return render(request, 'lms/entregas/detalle.html', context)

from .gamificacion_utils import (
    inicializar_insignias, obtener_estadisticas_usuario,
    actualizar_puntaje, obtener_puntaje_usuario
)

@login_required
def dashboard_gamificacion(request):
    """Dashboard con gamificación del usuario"""
    estadisticas = obtener_estadisticas_usuario(request.user)
    
    # Obtener cursos con progreso
    cursos_con_progreso = []
    for curso in Curso.objects.all():
        progreso, created = ProgresoCurso.objects.get_or_create(
            usuario=request.user,
            curso=curso
        )
        if progreso.practicas_completadas > 0 or progreso.evaluaciones_completadas > 0:
            cursos_con_progreso.append({
                'curso': curso,
                'progreso': progreso,
            })
    
    context = {
        'estadisticas': estadisticas,
        'cursos_con_progreso': cursos_con_progreso,
        'total_cursos': Curso.objects.count(),
        'total_recursos': RecursoEducativo.objects.count(),
    }
    return render(request, 'lms/estudiante/dashboard_gamificacion.html', context)

@login_required
def mis_insignias(request):
    """Vista para ver todas las insignias del usuario"""
    insignias = InsigniaUsuario.objects.filter(
        usuario=request.user
    ).select_related('insignia').order_by('-fecha_obtenida')
    
    todas_insignias = Insignia.objects.filter(is_active=True)
    
    context = {
        'insignias_obtenidas': insignias,
        'todas_insignias': todas_insignias,
        'total_obtenidas': insignias.count(),
        'total_disponibles': todas_insignias.count(),
    }
    return render(request, 'lms/estudiante/insignias.html', context)

@login_required
def ranking_usuarios(request):
    """Vista para ver el ranking de usuarios"""
    ranking = PuntajeUsuario.objects.select_related('usuario').order_by('-puntos_totales')[:50]
    
    # Agregar posición
    for idx, item in enumerate(ranking, 1):
        item.posicion = idx
    
    context = {
        'ranking': ranking,
    }
    return render(request, 'lms/estudiante/ranking.html', context)

from .gamificacion_utils import (
    inicializar_insignias, obtener_estadisticas_usuario,
    actualizar_puntaje, obtener_puntaje_usuario
)

@login_required
def dashboard_gamificacion(request):
    """Dashboard con gamificación del usuario"""
    estadisticas = obtener_estadisticas_usuario(request.user)
    
    # Obtener cursos con progreso
    cursos_con_progreso = []
    for curso in Curso.objects.all():
        progreso, created = ProgresoCurso.objects.get_or_create(
            usuario=request.user,
            curso=curso
        )
        if progreso.practicas_completadas > 0 or progreso.evaluaciones_completadas > 0:
            cursos_con_progreso.append({
                'curso': curso,
                'progreso': progreso,
            })
    
    context = {
        'estadisticas': estadisticas,
        'cursos_con_progreso': cursos_con_progreso,
        'total_cursos': Curso.objects.count(),
        'total_recursos': RecursoEducativo.objects.count(),
    }
    return render(request, 'lms/estudiante/dashboard_gamificacion.html', context)

@login_required
def mis_insignias(request):
    """Vista para ver todas las insignias del usuario"""
    insignias = InsigniaUsuario.objects.filter(
        usuario=request.user
    ).select_related('insignia').order_by('-fecha_obtenida')
    
    todas_insignias = Insignia.objects.filter(is_active=True)
    
    context = {
        'insignias_obtenidas': insignias,
        'todas_insignias': todas_insignias,
        'total_obtenidas': insignias.count(),
        'total_disponibles': todas_insignias.count(),
    }
    return render(request, 'lms/estudiante/insignias.html', context)

@login_required
def ranking_usuarios(request):
    """Vista para ver el ranking de usuarios"""
    ranking = PuntajeUsuario.objects.select_related('usuario').order_by('-puntos_totales')[:50]
    
    # Agregar posición
    for idx, item in enumerate(ranking, 1):
        item.posicion = idx
    
    context = {
        'ranking': ranking,
    }
    return render(request, 'lms/estudiante/ranking.html', context)

from .gamificacion_utils import (
    inicializar_insignias, obtener_estadisticas_usuario,
    actualizar_puntaje, obtener_puntaje_usuario
)

@login_required
def dashboard_gamificacion(request):
    """Dashboard con gamificación del usuario"""
    estadisticas = obtener_estadisticas_usuario(request.user)
    
    # Obtener cursos con progreso
    cursos_con_progreso = []
    for curso in Curso.objects.all():
        progreso, created = ProgresoCurso.objects.get_or_create(
            usuario=request.user,
            curso=curso
        )
        if progreso.practicas_completadas > 0 or progreso.evaluaciones_completadas > 0:
            cursos_con_progreso.append({
                'curso': curso,
                'progreso': progreso,
            })
    
    context = {
        'estadisticas': estadisticas,
        'cursos_con_progreso': cursos_con_progreso,
        'total_cursos': Curso.objects.count(),
        'total_recursos': RecursoEducativo.objects.count(),
    }
    return render(request, 'lms/estudiante/dashboard_gamificacion.html', context)

@login_required
def mis_insignias(request):
    """Vista para ver todas las insignias del usuario"""
    insignias = InsigniaUsuario.objects.filter(
        usuario=request.user
    ).select_related('insignia').order_by('-fecha_obtenida')
    
    todas_insignias = Insignia.objects.filter(is_active=True)
    
    context = {
        'insignias_obtenidas': insignias,
        'todas_insignias': todas_insignias,
        'total_obtenidas': insignias.count(),
        'total_disponibles': todas_insignias.count(),
    }
    return render(request, 'lms/estudiante/insignias.html', context)

@login_required
def ranking_usuarios(request):
    """Vista para ver el ranking de usuarios"""
    ranking = PuntajeUsuario.objects.select_related('usuario').order_by('-puntos_totales')[:50]
    
    # Agregar posición
    for idx, item in enumerate(ranking, 1):
        item.posicion = idx
    
    context = {
        'ranking': ranking,
    }
    return render(request, 'lms/estudiante/ranking.html', context)
