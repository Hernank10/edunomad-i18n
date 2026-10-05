# -*- coding: utf-8 -*-
"""Vistas del panel del profesor."""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from apps.core.models import (
    Curso, Practica, Evaluacion, PerfilUsuario, ProgresoCurso,
    Certificacion, RecursoEducativo, Notificacion,
)
from apps.language_practice.models import Course as LPCourse, Lesson as LPLesson
from apps.core.forms_profesor import (
    CursoForm, LeccionForm, PracticaForm, EvaluacionForm,
)


ROLES_DOCENTES = ("PROFESOR", "ADMIN", "SUPERUSUARIO")


def solo_profesor(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        perfil = PerfilUsuario.objects.filter(usuario=request.user).first()
        if not perfil or perfil.rol not in ROLES_DOCENTES:
            messages.error(request, "Acceso restringido a profesores.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def _cursos_del_profesor(user):
    perfil = PerfilUsuario.objects.filter(usuario=user).first()
    if perfil and perfil.rol in ("ADMIN", "SUPERUSUARIO"):
        return Curso.objects.all()
    if perfil:
        return perfil.cursos_impartidos.all()
    return Curso.objects.none()


# ============================================================
# Dashboard
# ============================================================
@solo_profesor
def profesor_dashboard(request):
    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))

    estudiantes_qs = PerfilUsuario.objects.filter(
        rol="ESTUDIANTE", cursos_inscritos__id__in=curso_ids,
    ).distinct()

    practicas = Practica.objects.filter(curso_id__in=curso_ids)
    evaluaciones = Evaluacion.objects.filter(curso_id__in=curso_ids)
    certificaciones = Certificacion.objects.filter(curso_id__in=curso_ids)

    context = {
        "total_cursos": cursos.count(),
        "total_estudiantes": estudiantes_qs.count(),
        "total_practicas": practicas.count(),
        "total_evaluaciones": evaluaciones.count(),
        "total_certificaciones": certificaciones.count(),
        "cursos_recientes": cursos.order_by("-fecha_creacion")[:5],
    }
    return render(request, "lms/profesor/dashboard.html", context)


# ============================================================
# CRUD Cursos
# ============================================================
@solo_profesor
def profesor_cursos_lista(request):
    cursos = _cursos_del_profesor(request.user).order_by("-fecha_creacion")
    return render(request, "lms/profesor/cursos_lista.html", {"cursos": cursos})


@solo_profesor
def profesor_curso_detalle(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    lp_course = LPCourse.objects.filter(title=curso.titulo).first()
    lecciones = LPLesson.objects.filter(course=lp_course).order_by("order") if lp_course else []
    return render(request, "lms/profesor/curso_detalle.html", {
        "curso": curso,
        "lecciones": lecciones,
        "practicas": curso.practicas.all(),
        "evaluaciones": curso.evaluaciones.all(),
        "recursos": curso.recursos.all(),
    })


@solo_profesor
def profesor_curso_nuevo(request):
    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            perfil.cursos_impartidos.add(curso)
            messages.success(request, "Curso creado correctamente.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        form = CursoForm()
    return render(request, "lms/profesor/curso_form.html", {
        "form": form, "accion": "Crear", "curso": None,
    })


@solo_profesor
def profesor_curso_editar(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    if request.method == "POST":
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, "Curso actualizado.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        form = CursoForm(instance=curso)
    return render(request, "lms/profesor/curso_form.html", {
        "form": form, "accion": "Editar", "curso": curso,
    })


@solo_profesor
def profesor_curso_eliminar(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    if request.method == "POST":
        curso.delete()
        messages.success(request, "Curso eliminado.")
        return redirect("profesor_cursos_lista")
    return render(request, "lms/profesor/confirmar_eliminar.html", {
        "objeto": curso, "tipo": "curso",
        "volver_url": "profesor_cursos_lista",
        "volver_arg": None,
    })


# ============================================================
# CRUD Lecciones (language_practice.Lesson)
# ============================================================
@solo_profesor
def profesor_leccion_nueva(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    lp_course = LPCourse.objects.filter(title=curso.titulo).first()
    if not lp_course:
        lp_course = LPCourse.objects.create(
            title=curso.titulo, language="Español",
            level=curso.nivel[:10], description=curso.descripcion,
        )
    if request.method == "POST":
        form = LeccionForm(request.POST)
        if form.is_valid():
            lec = form.save(commit=False)
            lec.course = lp_course
            lec.save()
            messages.success(request, "Lección creada.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        ultimo = LPLesson.objects.filter(course=lp_course).aggregate(
            m=Count("id"))["m"] or 0
        form = LeccionForm(initial={"order": ultimo + 1})
    return render(request, "lms/profesor/leccion_form.html", {
        "form": form, "accion": "Crear", "curso": curso, "leccion": None,
    })


@solo_profesor
def profesor_leccion_editar(request, leccion_id):
    leccion = get_object_or_404(LPLesson, id=leccion_id)
    curso = Curso.objects.filter(titulo=leccion.course.title).first()
    if not curso or curso not in _cursos_del_profesor(request.user):
        messages.error(request, "No tienes permiso sobre esta lección.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = LeccionForm(request.POST, instance=leccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Lección actualizada.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        form = LeccionForm(instance=leccion)
    return render(request, "lms/profesor/leccion_form.html", {
        "form": form, "accion": "Editar", "curso": curso, "leccion": leccion,
    })


@solo_profesor
def profesor_leccion_eliminar(request, leccion_id):
    leccion = get_object_or_404(LPLesson, id=leccion_id)
    curso = Curso.objects.filter(titulo=leccion.course.title).first()
    if not curso or curso not in _cursos_del_profesor(request.user):
        messages.error(request, "No tienes permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        leccion.delete()
        messages.success(request, "Lección eliminada.")
        return redirect("profesor_curso_detalle", curso_id=curso.id)
    return render(request, "lms/profesor/confirmar_eliminar.html", {
        "objeto": leccion, "tipo": "lección",
        "volver_url": "profesor_curso_detalle",
        "volver_arg": curso.id,
    })


# ============================================================
# CRUD Practicas
# ============================================================
@solo_profesor
def profesor_practica_nueva(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    if request.method == "POST":
        form = PracticaForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.curso = curso
            p.save()
            messages.success(request, "Práctica creada.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        form = PracticaForm()
    return render(request, "lms/profesor/practica_form.html", {
        "form": form, "accion": "Crear", "curso": curso, "practica": None,
    })


@solo_profesor
def profesor_practica_editar(request, practica_id):
    practica = get_object_or_404(Practica, id=practica_id)
    if practica.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = PracticaForm(request.POST, instance=practica)
        if form.is_valid():
            form.save()
            messages.success(request, "Práctica actualizada.")
            return redirect("profesor_curso_detalle", curso_id=practica.curso.id)
    else:
        form = PracticaForm(instance=practica)
    return render(request, "lms/profesor/practica_form.html", {
        "form": form, "accion": "Editar", "curso": practica.curso, "practica": practica,
    })


@solo_profesor
def profesor_practica_eliminar(request, practica_id):
    practica = get_object_or_404(Practica, id=practica_id)
    curso = practica.curso
    if curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        practica.delete()
        messages.success(request, "Práctica eliminada.")
        return redirect("profesor_curso_detalle", curso_id=curso.id)
    return render(request, "lms/profesor/confirmar_eliminar.html", {
        "objeto": practica, "tipo": "práctica",
        "volver_url": "profesor_curso_detalle",
        "volver_arg": curso.id,
    })


# ============================================================
# CRUD Evaluaciones
# ============================================================
@solo_profesor
def profesor_evaluacion_nueva(request, curso_id):
    curso = get_object_or_404(_cursos_del_profesor(request.user), id=curso_id)
    if request.method == "POST":
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            e = form.save(commit=False)
            e.curso = curso
            e.save()
            messages.success(request, "Evaluación creada.")
            return redirect("profesor_curso_detalle", curso_id=curso.id)
    else:
        form = EvaluacionForm()
    return render(request, "lms/profesor/evaluacion_form.html", {
        "form": form, "accion": "Crear", "curso": curso, "evaluacion": None,
    })


@solo_profesor
def profesor_evaluacion_editar(request, evaluacion_id):
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    if evaluacion.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = EvaluacionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Evaluación actualizada.")
            return redirect("profesor_curso_detalle", curso_id=evaluacion.curso.id)
    else:
        form = EvaluacionForm(instance=evaluacion)
    return render(request, "lms/profesor/evaluacion_form.html", {
        "form": form, "accion": "Editar", "curso": evaluacion.curso, "evaluacion": evaluacion,
    })


@solo_profesor
def profesor_evaluacion_eliminar(request, evaluacion_id):
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    curso = evaluacion.curso
    if curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        evaluacion.delete()
        messages.success(request, "Evaluación eliminada.")
        return redirect("profesor_curso_detalle", curso_id=curso.id)
    return render(request, "lms/profesor/confirmar_eliminar.html", {
        "objeto": evaluacion, "tipo": "evaluación",
        "volver_url": "profesor_curso_detalle",
        "volver_arg": curso.id,
    })


# ============================================================
# Estudiantes / Certificaciones
# ============================================================
@solo_profesor
def profesor_estudiantes_lista(request):
    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))
    perfiles = PerfilUsuario.objects.filter(
        rol="ESTUDIANTE", cursos_inscritos__id__in=curso_ids,
    ).distinct().select_related("usuario")
    data = []
    for p in perfiles:
        progresos = ProgresoCurso.objects.filter(
            usuario=p.usuario, curso_id__in=curso_ids,
        )
        data.append({
            "perfil": p,
            "num_cursos": progresos.count(),
            "completados": progresos.filter(completado=True).count(),
        })
    return render(request, "lms/profesor/estudiantes_lista.html", {
        "estudiantes": data,
    })


@solo_profesor
def profesor_estudiante_detalle(request, perfil_id):
    perfil = get_object_or_404(PerfilUsuario, id=perfil_id, rol="ESTUDIANTE")
    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))
    progresos = ProgresoCurso.objects.filter(
        usuario=perfil.usuario, curso_id__in=curso_ids,
    ).select_related("curso")
    certificaciones = Certificacion.objects.filter(
        usuario=perfil.usuario, curso_id__in=curso_ids,
    )
    return render(request, "lms/profesor/estudiante_detalle.html", {
        "perfil": perfil,
        "progresos": progresos,
        "certificaciones": certificaciones,
    })


@solo_profesor
def profesor_certificaciones_lista(request):
    cursos = _cursos_del_profesor(request.user)
    certs = Certificacion.objects.filter(
        curso__in=cursos,
    ).select_related("usuario", "curso").order_by("-fecha_inicio")
    return render(request, "lms/profesor/certificaciones_lista.html", {
        "certificaciones": certs,
    })
