# -*- coding: utf-8 -*-
"""Generacion de certificados PDF con xhtml2pdf + QR."""
from pathlib import Path
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string


def _get_dirs():
    root = Path(getattr(settings, "CERTIFICADOS_ROOT",
                        r"E:\02_proyectos\eduNomad\_certificados"))
    pdf_dir = root / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return root, pdf_dir


def ruta_pdf(cert):
    """Devuelve la ruta absoluta del PDF del certificado."""
    _, pdf_dir = _get_dirs()
    nombre = "cert_{}_{}.pdf".format(cert.id, cert.codigo_verificacion or "sincodigo")
    return pdf_dir / nombre


def _generar_qr_datauri(texto):
    """Genera un QR como data-URI base64 listo para meter en HTML."""
    try:
        import qrcode
    except ImportError:
        return ""
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(texto)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        import base64
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return "data:image/png;base64,{}".format(b64)
    except Exception:
        return ""


def construir_contexto(cert):
    """Contexto para el template del diploma."""
    from django.contrib.auth import get_user_model
    from django.urls import reverse

    curso = cert.curso
    perfil_estudiante = getattr(cert.usuario, "perfil", None)

    # Profesor asignado al curso
    profesor = None
    if hasattr(curso, "profesores"):
        profesor = curso.profesores.select_related("usuario").first()

    # Administrador principal
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True, is_active=True).order_by("id").first()

    # URL publica de verificacion
    codigo = cert.codigo_verificacion or ""
    url_verificacion = ""
    try:
        ruta = reverse("verificar_certificado_codigo", kwargs={"codigo": codigo})
        # Intentar URL absoluta con el host actual
        url_verificacion = ruta
    except Exception:
        url_verificacion = "/es/verificar/{}/".format(codigo)

    # QR data-URI (apunta a la URL de verificacion relativa — el PDF se abrira local)
    qr_uri = _generar_qr_datauri(url_verificacion) if codigo else ""

    return {
        "cert": cert,
        "curso": curso,
        "estudiante": cert.usuario,
        "perfil_estudiante": perfil_estudiante,
        "profesor": profesor.usuario if profesor else None,
        "admin": admin,
        "codigo": codigo,
        "url_verificacion": url_verificacion,
        "qr_uri": qr_uri,
        "fecha": cert.fecha_completado or cert.fecha_inicio,
        "puntaje": cert.puntaje_obtenido,
        "porcentaje": cert.porcentaje,
    }


def render_html(cert):
    """Renderiza el HTML del diploma."""
    ctx = construir_contexto(cert)
    return render_to_string("lms/certificados/diploma.html", ctx)


def generar_pdf(cert, forzar=False):
    """Genera (o regenera) el PDF del certificado.

    Devuelve la ruta absoluta del PDF.
    """
    ruta = ruta_pdf(cert)

    if ruta.exists() and not forzar:
        return ruta

    try:
        from xhtml2pdf import pisa
    except ImportError:
        raise RuntimeError(
            "xhtml2pdf no esta instalado. Ejecuta: pip install xhtml2pdf"
        )

    html = render_html(cert)

    buf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buf, encoding="utf-8")

    if pisa_status.err:
        raise RuntimeError("Error generando PDF: {}".format(pisa_status.err))

    ruta.write_bytes(buf.getvalue())
    return ruta