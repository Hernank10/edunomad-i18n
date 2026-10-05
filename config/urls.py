# -*- coding: utf-8 -*-
"""URLs raiz de eduNomad.

- SIN prefijo de idioma: /i18n/, /admin/, /api/...
- CON prefijo de idioma: /es/, /en/, /pt/, ... (todas las vistas web)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from apps.core.views import (
    home, explorar_recursos, detalle_curso,
    lista_cursos, detalle_practica, detalle_evaluacion,
    subir_archivo, listar_entregas, descargar_entrega,
    eliminar_entrega, detalle_entrega,
    enviar_practica, enviar_evaluacion,
    mis_certificaciones, ver_certificacion, progreso_curso,
    dashboard_gamificacion, mis_insignias, ranking_usuarios,
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

    # Recursos y cursos
    path('recursos/', explorar_recursos, name='explorar_recursos'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', detalle_curso, name='detalle_curso'),

    # Practicas y evaluaciones
    path('practicas/<int:practica_id>/', detalle_practica, name='detalle_practica'),
    path('evaluaciones/<int:evaluacion_id>/', detalle_evaluacion, name='detalle_evaluacion'),

    # Certificaciones y progreso
    path('certificaciones/', mis_certificaciones, name='mis_certificaciones'),
    path('certificaciones/<int:certificacion_id>/', ver_certificacion, name='ver_certificacion'),
    path('progreso/<int:curso_id>/', progreso_curso, name='progreso_curso'),

    # Entregas
    path('entregas/', listar_entregas, name='listar_entregas'),
    path('entregas/<int:entrega_id>/', detalle_entrega, name='detalle_entrega'),

    # Gamificacion
    path('insignias/', mis_insignias, name='mis_insignias'),
    path('ranking/', ranking_usuarios, name='ranking_usuarios'),
)
