# -*- coding: utf-8 -*-
"""URLs raiz de eduNomad.

- SIN prefijo de idioma: /i18n/, /admin/, /api/...
- CON prefijo de idioma: /es/, /en/, /pt/, ... (todas las vistas web)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from apps.core.views import (
    ver_recurso, detalle_leccion, ver_certificado, ver_certificado_pdf, verificar_certificado,
    home, explorar_recursos, detalle_curso,
    lista_cursos, detalle_practica, detalle_evaluacion,
    subir_archivo, listar_entregas, descargar_entrega,
    eliminar_entrega, detalle_entrega,
    enviar_practica, enviar_evaluacion,
    mis_certificaciones, ver_certificacion, progreso_curso,
    dashboard_gamificacion, mis_insignias, ranking_usuarios,
)
from apps.core.views_profesor import (
    profesor_practica_detalle, profesor_evaluacion_detalle,
    profesor_ejercicio_nuevo_practica, profesor_ejercicio_nuevo_evaluacion,
    profesor_ejercicio_editar, profesor_ejercicio_eliminar,
    profesor_inscribirse_curso,
    profesor_actividad,
    profesor_dashboard,
    profesor_cursos_lista, profesor_curso_detalle,
    profesor_curso_nuevo, profesor_curso_editar, profesor_curso_eliminar,
    profesor_leccion_nueva, profesor_leccion_editar, profesor_leccion_eliminar, profesor_leccion_detalle,
    profesor_practica_nueva, profesor_practica_editar, profesor_practica_eliminar,
    profesor_evaluacion_nueva, profesor_evaluacion_editar, profesor_evaluacion_eliminar,
    profesor_estudiantes_lista, profesor_estudiante_detalle,
    profesor_certificaciones_lista,
    profesor_ranking,
)
from apps.core.views_auth import (
    register_view, login_view, logout_view,
    perfil_view, dashboard_estudiante,
)


# ============================================================
# Rutas SIN prefijo de idioma
# ============================================================
urlpatterns = [
    # set_language (cambio de idioma)
    path('i18n/', include('django.conf.urls.i18n')),

    # Admin
    path('admin/', admin.site.urls),

    # API REST (router DRF: /api/recursos/, /api/cursos/...)
    path('api/', include('apps.core.urls')),

    # Endpoints API sueltos
    path('api/enviar_practica/<int:practica_id>/', enviar_practica, name='enviar_practica'),
    path('api/enviar_evaluacion/<int:evaluacion_id>/', enviar_evaluacion, name='enviar_evaluacion'),
    path('api/subir_archivo/', subir_archivo, name='subir_archivo'),
    path('api/descargar_entrega/<int:entrega_id>/', descargar_entrega, name='descargar_entrega'),
    path('api/eliminar_entrega/<int:entrega_id>/', eliminar_entrega, name='eliminar_entrega'),
]


# ============================================================
# Rutas CON prefijo de idioma (i18n_patterns)
# ============================================================
urlpatterns += i18n_patterns(
    # Pagina principal
    path('', home, name='home'),

    # Autenticacion
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    path('dashboard/', dashboard_gamificacion, name='dashboard'),
    path('dashboard-estudiante/', dashboard_estudiante, name='dashboard_estudiante'),

    # Recursos y cursos
    path('recursos/', explorar_recursos, name='explorar_recursos'),
    path('recurso/<int:recurso_id>/', ver_recurso, name='ver_recurso'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', detalle_curso, name='detalle_curso'),
    path('lecciones/<int:leccion_id>/', detalle_leccion, name='detalle_leccion'),

    # Practicas y evaluaciones
    path('practicas/<int:practica_id>/', detalle_practica, name='detalle_practica'),
    path('evaluaciones/<int:evaluacion_id>/', detalle_evaluacion, name='detalle_evaluacion'),

    # Certificaciones y progreso
    path('certificaciones/', mis_certificaciones, name='mis_certificaciones'),
    path('certificaciones/<int:certificacion_id>/', ver_certificacion, name='ver_certificacion'),
    path('certificado/<int:certificacion_id>/diploma/', ver_certificado, name='ver_certificado'),
    path('certificado/<int:certificacion_id>/pdf/', ver_certificado_pdf, name='ver_certificado_pdf'),
    path('verificar/', verificar_certificado, name='verificar_certificado'),
    path('verificar/<str:codigo>/', verificar_certificado, name='verificar_certificado_codigo'),
    path('progreso/<int:curso_id>/', progreso_curso, name='progreso_curso'),

    # Entregas
    path('entregas/', listar_entregas, name='listar_entregas'),
    path('entregas/<int:entrega_id>/', detalle_entrega, name='detalle_entrega'),

    # Gamificacion
    path('insignias/', mis_insignias, name='mis_insignias'),

    # ============================================================
    # Panel del Profesor
    # ============================================================
    path('profesor/', profesor_dashboard, name='profesor_dashboard'),
    path('profesor/cursos/', profesor_cursos_lista, name='profesor_cursos_lista'),
    path('profesor/cursos/nuevo/', profesor_curso_nuevo, name='profesor_curso_nuevo'),
    path('profesor/cursos/<int:curso_id>/', profesor_curso_detalle, name='profesor_curso_detalle'),
    path('profesor/cursos/<int:curso_id>/editar/', profesor_curso_editar, name='profesor_curso_editar'),
    path('profesor/cursos/<int:curso_id>/eliminar/', profesor_curso_eliminar, name='profesor_curso_eliminar'),
    path('profesor/cursos/<int:curso_id>/lecciones/nueva/', profesor_leccion_nueva, name='profesor_leccion_nueva'),
    path('profesor/lecciones/<int:leccion_id>/detalle/', profesor_leccion_detalle, name='profesor_leccion_detalle'),
    path('profesor/lecciones/<int:leccion_id>/editar/', profesor_leccion_editar, name='profesor_leccion_editar'),
    path('profesor/lecciones/<int:leccion_id>/eliminar/', profesor_leccion_eliminar, name='profesor_leccion_eliminar'),
    path('profesor/cursos/<int:curso_id>/practicas/nueva/', profesor_practica_nueva, name='profesor_practica_nueva'),
    path('profesor/practicas/<int:practica_id>/editar/', profesor_practica_editar, name='profesor_practica_editar'),
    path('profesor/practicas/<int:practica_id>/eliminar/', profesor_practica_eliminar, name='profesor_practica_eliminar'),
    path('profesor/cursos/<int:curso_id>/evaluaciones/nueva/', profesor_evaluacion_nueva, name='profesor_evaluacion_nueva'),
    path('profesor/evaluaciones/<int:evaluacion_id>/editar/', profesor_evaluacion_editar, name='profesor_evaluacion_editar'),
    path('profesor/evaluaciones/<int:evaluacion_id>/eliminar/', profesor_evaluacion_eliminar, name='profesor_evaluacion_eliminar'),
    path('profesor/estudiantes/', profesor_estudiantes_lista, name='profesor_estudiantes_lista'),
    path('profesor/estudiantes/<int:perfil_id>/', profesor_estudiante_detalle, name='profesor_estudiante_detalle'),
    path('profesor/certificaciones/', profesor_certificaciones_lista, name='profesor_certificaciones_lista'),
    path('profesor/ranking/', profesor_ranking, name='profesor_ranking'),
    path('profesor/actividad/', profesor_actividad, name='profesor_actividad'),
    path('profesor/practicas/<int:practica_id>/detalle/', profesor_practica_detalle, name='profesor_practica_detalle'),
    path('profesor/evaluaciones/<int:evaluacion_id>/detalle/', profesor_evaluacion_detalle, name='profesor_evaluacion_detalle'),
    path('profesor/practicas/<int:practica_id>/ejercicios/nuevo/', profesor_ejercicio_nuevo_practica, name='profesor_ejercicio_nuevo_practica'),
    path('profesor/evaluaciones/<int:evaluacion_id>/ejercicios/nuevo/', profesor_ejercicio_nuevo_evaluacion, name='profesor_ejercicio_nuevo_evaluacion'),
    path('profesor/ejercicios/<int:ejercicio_id>/editar/', profesor_ejercicio_editar, name='profesor_ejercicio_editar'),
    path('profesor/ejercicios/<int:ejercicio_id>/eliminar/', profesor_ejercicio_eliminar, name='profesor_ejercicio_eliminar'),
    path('profesor/cursos/<int:curso_id>/inscribirme/', profesor_inscribirse_curso, name='profesor_inscribirse_curso'),

    path('ranking/', ranking_usuarios, name='ranking_usuarios'),
)
