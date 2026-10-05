# -*- coding: utf-8 -*-
"""Vistas del panel del profesor."""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from apps.core.models import (
    Curso, Practica, Evaluacion, EjercicioInteractivo,
    PerfilUsuario, ProgresoCurso,
    Certificacion, RecursoEducativo, Notificacion,
)
from apps.language_practice.models import Course as LPCourse, Lesson as LPLesson
from apps.core.forms_profesor import (
    CursoForm, LeccionForm, PracticaForm, EvaluacionForm,
    EjercicioInteractivoForm,
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


# ============================================================
# Detalle de practica/evaluacion con sus ejercicios
# ============================================================
@solo_profesor
def profesor_practica_detalle(request, practica_id):
    practica = get_object_or_404(Practica, id=practica_id)
    if practica.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    ejercicios = practica.ejercicios.all().order_by("orden")
    return render(request, "lms/profesor/practica_detalle.html", {
        "practica": practica,
        "curso": practica.curso,
        "ejercicios": ejercicios,
    })


@solo_profesor
def profesor_evaluacion_detalle(request, evaluacion_id):
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    if evaluacion.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    ejercicios = evaluacion.ejercicios.all().order_by("orden")
    return render(request, "lms/profesor/evaluacion_detalle.html", {
        "evaluacion": evaluacion,
        "curso": evaluacion.curso,
        "ejercicios": ejercicios,
    })


@solo_profesor
def profesor_ejercicio_nuevo_practica(request, practica_id):
    practica = get_object_or_404(Practica, id=practica_id)
    if practica.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = EjercicioInteractivoForm(request.POST)
        if form.is_valid():
            ej = form.save(commit=False)
            ej.practica = practica
            ej.save()
            messages.success(request, "Ejercicio creado.")
            return redirect("profesor_practica_detalle", practica_id=practica.id)
    else:
        form = EjercicioInteractivoForm(initial={"orden": practica.ejercicios.count() + 1, "is_active": True})
    return render(request, "lms/profesor/ejercicio_form.html", {
        "form": form, "accion": "Crear",
        "curso": practica.curso, "tipo_entidad": "practica",
        "entidad": practica, "ejercicio": None,
    })


@solo_profesor
def profesor_ejercicio_nuevo_evaluacion(request, evaluacion_id):
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)
    if evaluacion.curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = EjercicioInteractivoForm(request.POST)
        if form.is_valid():
            ej = form.save(commit=False)
            ej.evaluacion = evaluacion
            ej.save()
            messages.success(request, "Ejercicio creado.")
            return redirect("profesor_evaluacion_detalle", evaluacion_id=evaluacion.id)
    else:
        form = EjercicioInteractivoForm(initial={"orden": evaluacion.ejercicios.count() + 1, "is_active": True})
    return render(request, "lms/profesor/ejercicio_form.html", {
        "form": form, "accion": "Crear",
        "curso": evaluacion.curso, "tipo_entidad": "evaluacion",
        "entidad": evaluacion, "ejercicio": None,
    })


@solo_profesor
def profesor_ejercicio_editar(request, ejercicio_id):
    ej = get_object_or_404(EjercicioInteractivo, id=ejercicio_id)
    curso = ej.practica.curso if ej.practica else (ej.evaluacion.curso if ej.evaluacion else None)
    if not curso or curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if request.method == "POST":
        form = EjercicioInteractivoForm(request.POST, instance=ej)
        if form.is_valid():
            form.save()
            messages.success(request, "Ejercicio actualizado.")
            if ej.practica:
                return redirect("profesor_practica_detalle", practica_id=ej.practica.id)
            return redirect("profesor_evaluacion_detalle", evaluacion_id=ej.evaluacion.id)
    else:
        form = EjercicioInteractivoForm(instance=ej)
    tipo_entidad = "practica" if ej.practica else "evaluacion"
    entidad = ej.practica if ej.practica else ej.evaluacion
    return render(request, "lms/profesor/ejercicio_form.html", {
        "form": form, "accion": "Editar",
        "curso": curso, "tipo_entidad": tipo_entidad,
        "entidad": entidad, "ejercicio": ej,
    })


@solo_profesor
def profesor_ejercicio_eliminar(request, ejercicio_id):
    ej = get_object_or_404(EjercicioInteractivo, id=ejercicio_id)
    curso = ej.practica.curso if ej.practica else (ej.evaluacion.curso if ej.evaluacion else None)
    if not curso or curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")
    if ej.practica:
        volver_url = "profesor_practica_detalle"
        volver_arg = ej.practica.id
        arg_name = "practica_id"
    else:
        volver_url = "profesor_evaluacion_detalle"
        volver_arg = ej.evaluacion.id
        arg_name = "evaluacion_id"
    if request.method == "POST":
        ej.delete()
        messages.success(request, "Ejercicio eliminado.")
        kw = {arg_name: volver_arg}
        return redirect(volver_url, **kw)
    return render(request, "lms/profesor/confirmar_eliminar.html", {
        "objeto": ej, "tipo": "ejercicio",
        "volver_url": volver_url, "volver_arg": volver_arg,
    })


@solo_profesor
def profesor_inscribirse_curso(request, curso_id):
    if request.method != "POST":
        return redirect("profesor_curso_detalle", curso_id=curso_id)
    curso = get_object_or_404(Curso, id=curso_id)
    perfil = PerfilUsuario.objects.get(usuario=request.user)
    if perfil.cursos_inscritos.filter(id=curso.id).exists():
        perfil.cursos_inscritos.remove(curso)
        messages.info(request, "Te has desinscrito del curso.")
    else:
        perfil.cursos_inscritos.add(curso)
        ProgresoCurso.objects.get_or_create(usuario=request.user, curso=curso)
        messages.success(request, "Inscrito. Puedes acceder como estudiante.")
    return redirect("profesor_curso_detalle", curso_id=curso.id)


# ============================================================
# Estudiantes por curso + Ranking
# ============================================================
@solo_profesor
def profesor_estudiantes_lista(request):
    cursos = _cursos_del_profesor(request.user)

    cursos_data = []
    for curso in cursos:
        perfiles = PerfilUsuario.objects.filter(
            rol="ESTUDIANTE", cursos_inscritos=curso,
        ).select_related("usuario")

        ests = []
        for p in perfiles:
            prog = ProgresoCurso.objects.filter(usuario=p.usuario, curso=curso).first()
            cert = Certificacion.objects.filter(usuario=p.usuario, curso=curso).first()
            ests.append({
                "perfil": p,
                "puntaje": prog.puntaje_total if prog else 0,
                "completado": prog.completado if prog else False,
                "certificado": bool(cert),
            })

        ests.sort(key=lambda x: x["puntaje"], reverse=True)
        total = len(ests)
        completados = sum(1 for e in ests if e["completado"])
        promedio = round(sum(e["puntaje"] for e in ests) / total, 1) if total else 0

        cursos_data.append({
            "curso": curso,
            "estudiantes": ests,
            "total": total,
            "completados": completados,
            "promedio": promedio,
        })

    cursos_data.sort(key=lambda x: x["total"], reverse=True)
    return render(request, "lms/profesor/estudiantes_lista.html", {
        "cursos_data": cursos_data,
        "total_cursos": len(cursos_data),
        "total_estudiantes": sum(c["total"] for c in cursos_data),
    })


@solo_profesor
def profesor_ranking(request):
    from django.db.models import Sum, Count, Q

    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))
    curso_filtro = request.GET.get("curso")
    curso_actual = None

    if curso_filtro:
        try:
            cid = int(curso_filtro)
            if cid in curso_ids:
                curso_ids = [cid]
                curso_actual = Curso.objects.filter(id=cid).first()
        except ValueError:
            pass

    ranking = (
        ProgresoCurso.objects
        .filter(curso_id__in=curso_ids)
        .values("usuario_id", "usuario__username", "usuario__first_name",
                "usuario__last_name", "usuario__email")
        .annotate(
            puntaje_total=Sum("puntaje_total"),
            cursos_count=Count("id"),
            completados=Count("id", filter=Q(completado=True)),
        )
        .order_by("-puntaje_total")[:100]
    )

    ranking_lista = []
    for i, r in enumerate(ranking, 1):
        certs = Certificacion.objects.filter(
            usuario_id=r["usuario_id"], curso_id__in=curso_ids,
            estado="COMPLETADO",
        ).count()
        nombre = (r["usuario__first_name"] + " " + r["usuario__last_name"]).strip()
        ranking_lista.append({
            "posicion": i,
            "username": r["usuario__username"],
            "nombre": nombre or r["usuario__username"],
            "email": r["usuario__email"],
            "puntaje_total": round(r["puntaje_total"] or 0, 1),
            "cursos_count": r["cursos_count"],
            "completados": r["completados"],
            "certificados": certs,
        })

    return render(request, "lms/profesor/ranking.html", {
        "ranking": ranking_lista,
        "cursos": cursos,
        "curso_actual": curso_actual,
    })


# ============================================================
# Actividad reciente del docente
# ============================================================
from datetime import timedelta
from django.utils import timezone


def _construir_actividad(request, limite=50):
    """Construye la lista de actividad reciente para los cursos del profe."""
    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))
    curso_map = {c.id: c for c in cursos}
    user_map = {}

    actividades = []
    hace_30 = timezone.now() - timedelta(days=30)

    # 1) Progreso reciente de estudiantes
    try:
        from apps.core.models import EntregaArchivo
        entregas_recientes = True
    except Exception:
        entregas_recientes = False

    progresos = ProgresoCurso.objects.filter(
        curso_id__in=curso_ids,
        ultimo_acceso__gte=hace_30,
    ).select_related("usuario", "curso").order_by("-ultimo_acceso")[:40]

    for p in progresos:
        user = p.usuario
        user_map[user.id] = user
        if p.completado:
            txt = "{} completo el curso \"{}\"".format(user.username, p.curso.titulo[:60])
            ico = "fa-check-circle"
            col = "success"
        else:
            txt = "{} avanzo en \"{}\" ({}% puntaje)".format(
                user.username, p.curso.titulo[:60], round(p.puntaje_total, 1))
            ico = "fa-user-graduate"
            col = "info"
        actividades.append({
            "fecha": p.ultimo_acceso,
            "tipo": "progreso",
            "icono": ico,
            "color": col,
            "texto": txt,
            "url_curso": p.curso.id,
            "username": user.username,
        })

    # 2) Certificaciones emitidas
    certs = Certificacion.objects.filter(
        curso_id__in=curso_ids,
        fecha_completado__gte=hace_30,
    ).select_related("usuario", "curso").order_by("-fecha_completado")[:30]

    for c in certs:
        if c.usuario_id not in user_map:
            user_map[c.usuario_id] = c.usuario
        actividades.append({
            "fecha": c.fecha_completado or c.fecha_inicio,
            "tipo": "certificado",
            "icono": "fa-certificate",
            "color": "warning",
            "texto": "Certificado emitido a {} en \"{}\"".format(
                c.usuario.username, c.curso.titulo[:60]),
            "url_cert": c.id,
            "url_curso": c.curso.id,
            "username": c.usuario.username,
        })

    # 3) Entregas de archivos
    if entregas_recientes:
        entregas = EntregaArchivo.objects.filter(
            practica__curso_id__in=curso_ids,
            fecha_entrega__gte=hace_30,
        ).select_related("usuario", "practica").order_by("-fecha_entrega")[:30]

        for e in entregas:
            if e.usuario_id not in user_map:
                user_map[e.usuario_id] = e.usuario
            titulo_prac = e.practica.titulo if e.practica else "practica"
            actividades.append({
                "fecha": e.fecha_entrega,
                "tipo": "entrega",
                "icono": "fa-file-upload",
                "color": "primary",
                "texto": "{} subio entrega \"{}\" de {}".format(
                    e.usuario.username, e.titulo[:40], titulo_prac[:50]),
                "url_curso": e.practica.curso_id if e.practica else None,
                "username": e.usuario.username,
            })

    # Ordenar por fecha desc y limitar
    actividades.sort(key=lambda x: x["fecha"] or timezone.now(), reverse=True)
    return actividades[:limite], curso_map, user_map


@solo_profesor
def profesor_actividad(request):
    """Timeline completo de actividad reciente."""
    actividades, _, _ = _construir_actividad(request, limite=100)

    # Contadores rapidos
    hace_7 = timezone.now() - timedelta(days=7)
    hace_30 = timezone.now() - timedelta(days=30)

    cursos = _cursos_del_profesor(request.user)
    curso_ids = list(cursos.values_list("id", flat=True))

    stats = {
        "progresos_7d": ProgresoCurso.objects.filter(
            curso_id__in=curso_ids, ultimo_acceso__gte=hace_7).count(),
        "progresos_30d": ProgresoCurso.objects.filter(
            curso_id__in=curso_ids, ultimo_acceso__gte=hace_30).count(),
        "certificados_7d": Certificacion.objects.filter(
            curso_id__in=curso_ids, fecha_completado__gte=hace_7).count(),
        "certificados_30d": Certificacion.objects.filter(
            curso_id__in=curso_ids, fecha_completado__gte=hace_30).count(),
    }

    return render(request, "lms/profesor/actividad.html", {
        "actividades": actividades,
        "stats": stats,
    })


@solo_profesor
def profesor_leccion_detalle(request, leccion_id):
    """Muestra la leccion con sus practicas, evaluaciones y ejercicios."""
    leccion = get_object_or_404(LPLesson, id=leccion_id)
    curso = Curso.objects.filter(titulo=leccion.course.title).first()
    if not curso or curso not in _cursos_del_profesor(request.user):
        messages.error(request, "Sin permiso.")
        return redirect("profesor_dashboard")

    practicas = Practica.objects.filter(leccion=leccion).order_by("orden")
    evaluaciones = Evaluacion.objects.filter(leccion=leccion).order_by("id")

    # Ejercicios por practica/evaluacion
    practicas_data = []
    for p in practicas:
        ejs = EjercicioInteractivo.objects.filter(practica=p).order_by("orden")
        practicas_data.append({"practica": p, "ejercicios": list(ejs)})

    evals_data = []
    for e in evaluaciones:
        ejs = EjercicioInteractivo.objects.filter(evaluacion=e).order_by("orden")
        evals_data.append({"evaluacion": e, "ejercicios": list(ejs)})

    # Recurso origen (buscar por nombre)
    recurso_origen = None
    titulo_norm = leccion.title.lower().strip()
    for r in curso.recursos.all():
        if titulo_norm in r.nombre_archivo.lower() or r.nombre_archivo.lower().startswith(titulo_norm[:30]):
            recurso_origen = r
            break

    return render(request, "lms/profesor/leccion_detalle.html", {
        "curso": curso,
        "leccion": leccion,
        "practicas_data": practicas_data,
        "evals_data": evals_data,
        "recurso_origen": recurso_origen,
    })
