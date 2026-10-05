from django.db import models
from django.utils.text import slugify

class RecursoEducativo(models.Model):
    nombre_archivo = models.CharField(max_length=500)
    ruta_completa = models.CharField(max_length=1000, unique=True)
    extension = models.CharField(max_length=20, blank=True, null=True)
    categoria = models.CharField(max_length=100, db_index=True)
    tipo_contenido = models.CharField(max_length=50, blank=True, null=True)
    tamanio_bytes = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()
    descripcion = models.TextField(blank=True, null=True)
    etiquetas = models.TextField(blank=True, null=True)
    importado_el = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['categoria', 'nombre_archivo']
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['nombre_archivo']),
        ]
    
    def __str__(self):
        return f"{self.categoria}: {self.nombre_archivo[:50]}"
    
    @property
    def tamanio_kb(self):
        return round(self.tamanio_bytes / 1024, 2)
    
    @property
    def tamanio_mb(self):
        return round(self.tamanio_bytes / (1024 * 1024), 2)


class Curso(models.Model):
    NIVELES = [
        ('PRIMARIA', 'Primaria'),
        ('SECUNDARIA', 'Secundaria'),
        ('BACHILLERATO', 'Bachillerato'),
        ('UNIVERSITARIO', 'Universitario'),
        ('POSGRADO', 'Posgrado'),
        ('LIBRE', 'Libre'),
    ]
    
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PUBLICADO', 'Publicado'),
        ('ARCHIVADO', 'Archivado'),
    ]
    
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100, db_index=True)
    nivel = models.CharField(max_length=20, choices=NIVELES, default='LIBRE')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    duracion_horas = models.IntegerField(default=10)
    recursos = models.ManyToManyField(RecursoEducativo, related_name='cursos', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    imagen_url = models.URLField(blank=True, null=True)
    palabras_clave = models.CharField(max_length=500, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['nivel']),
            models.Index(fields=['estado']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.titulo} - {self.nivel}"
    
    @property
    def total_recursos(self):
        return self.recursos.count()
    
    @property
    def tamanio_total_mb(self):
        total_bytes = self.recursos.aggregate(models.Sum('tamanio_bytes'))['tamanio_bytes__sum'] or 0
        return round(total_bytes / (1024 * 1024), 2)


class Practica(models.Model):
    TIPOS = [
        ('EJERCICIO', 'Ejercicio'),
        ('QUIZ', 'Quiz'),
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('REPASO', 'Repaso'),
    ]
    
    leccion = models.ForeignKey('language_practice.Lesson', on_delete=models.CASCADE, 
                                related_name='practicas', null=True, blank=True)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='practicas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='EJERCICIO')
    preguntas = models.JSONField(default=list, blank=True)
    puntaje_maximo = models.IntegerField(default=100)
    duracion_minutos = models.IntegerField(default=15)
    orden = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['orden', 'fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.curso.titulo[:30]}"


class Evaluacion(models.Model):
    TIPOS = [
        ('EXAMEN', 'Examen'),
        ('PRACTICA', 'Práctica'),
        ('PROYECTO', 'Proyecto'),
        ('FINAL', 'Final'),
    ]
    
    leccion = models.ForeignKey('language_practice.Lesson', on_delete=models.CASCADE,
                                related_name='evaluaciones', null=True, blank=True)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='evaluaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='EXAMEN')
    preguntas = models.JSONField(default=list, blank=True)
    puntaje_maximo = models.IntegerField(default=100)
    duracion_minutos = models.IntegerField(default=30)
    nota_minima = models.IntegerField(default=60)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.curso.titulo[:30]}"


class EjercicioInteractivo(models.Model):
    TIPOS = [
        ('OPCION_MULTIPLE', 'Opción Múltiple'),
        ('VERDADERO_FALSO', 'Verdadero/Falso'),
        ('COMPLETAR', 'Completar'),
        ('ORDENAR', 'Ordenar'),
        ('RELACIONAR', 'Relacionar'),
        ('TEXTO', 'Texto Libre'),
    ]
    
    practica = models.ForeignKey('Practica', on_delete=models.CASCADE, 
                                 related_name='ejercicios', null=True, blank=True)
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE,
                                   related_name='ejercicios', null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='OPCION_MULTIPLE')
    pregunta = models.TextField()
    opciones = models.JSONField(default=list, blank=True)
    respuesta_correcta = models.TextField()
    explicacion = models.TextField(blank=True, null=True)
    puntaje = models.IntegerField(default=5)
    orden = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.tipo}: {self.pregunta[:50]}..."


class EntregaArchivo(models.Model):
    TIPOS = [
        ('AUDIO', 'Audio'),
        ('IMAGEN', 'Imagen'),
        ('PDF', 'PDF'),
        ('DOCUMENTO', 'Documento'),
        ('VIDEO', 'Video'),
        ('OTRO', 'Otro'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('REVISION', 'En revisión'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='entregas')
    practica = models.ForeignKey('Practica', on_delete=models.CASCADE, null=True, blank=True, related_name='entregas')
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE, null=True, blank=True, related_name='entregas')
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo_archivo = models.CharField(max_length=20, choices=TIPOS, default='DOCUMENTO')
    archivo = models.FileField(upload_to='entregas/%Y/%m/%d/', max_length=500)
    nombre_original = models.CharField(max_length=255)
    tamanio_bytes = models.BigIntegerField(default=0)
    extension = models.CharField(max_length=10, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    comentario_profesor = models.TextField(blank=True, null=True)
    calificacion = models.FloatField(null=True, blank=True)
    
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_entrega']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['practica']),
            models.Index(fields=['evaluacion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo[:30]}"
    
    @property
    def tamanio_mb(self):
        return round(self.tamanio_bytes / (1024 * 1024), 2)
    
    @property
    def es_audio(self):
        return self.tipo_archivo == 'AUDIO' or self.extension.lower() in ['.mp3', '.wav', '.ogg', '.m4a']
    
    @property
    def es_imagen(self):
        return self.tipo_archivo == 'IMAGEN' or self.extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
    
    @property
    def es_pdf(self):
        return self.tipo_archivo == 'PDF' or self.extension.lower() == '.pdf'
    
    @property
    def es_video(self):
        return self.tipo_archivo == 'VIDEO' or self.extension.lower() in ['.mp4', '.avi', '.mov', '.wmv', '.flv']


class Certificacion(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('REVOCADO', 'Revocado'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='certificaciones')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='certificaciones')
    practica = models.ForeignKey('Practica', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificaciones')
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificaciones')
    
    puntaje_obtenido = models.FloatField(default=0.0)
    porcentaje = models.FloatField(default=0.0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    
    codigo_verificacion = models.CharField(max_length=100, unique=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_completado']
        unique_together = ['usuario', 'curso']
        verbose_name = 'Certificación'
        verbose_name_plural = 'Certificaciones'
    
    def save(self, *args, **kwargs):
        if not self.codigo_verificacion:
            import hashlib
            import time
            raw = f"{self.usuario_id}-{self.curso_id}-{time.time()}"
            self.codigo_verificacion = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo[:30]} - {self.estado}"


class ProgresoCurso(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='progresos')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='progresos')
    practicas_completadas = models.IntegerField(default=0)
    evaluaciones_completadas = models.IntegerField(default=0)
    puntaje_total = models.FloatField(default=0.0)
    lecciones_vistas = models.IntegerField(default=0)
    ultimo_acceso = models.DateTimeField(auto_now=True)
    completado = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['usuario', 'curso']
        ordering = ['-ultimo_acceso']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.curso.titulo[:30]}"


class Insignia(models.Model):
    TIPOS = [
        ('CURSO', 'Curso'),
        ('PRACTICA', 'Práctica'),
        ('EVALUACION', 'Evaluación'),
        ('RACHA', 'Racha'),
        ('ESPECIAL', 'Especial'),
        ('CERTIFICACION', 'Certificación'),
    ]
    
    NIVELES_INSIGNIA = [
        ('BRONCE', 'Bronce'),
        ('PLATA', 'Plata'),
        ('ORO', 'Oro'),
        ('DIAMANTE', 'Diamante'),
        ('EXPERTO', 'Experto'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    nivel = models.CharField(max_length=20, choices=NIVELES_INSIGNIA, default='BRONCE')
    icono = models.CharField(max_length=50, default='fa-star')
    color = models.CharField(max_length=20, default='#FFD700')
    puntos_requeridos = models.IntegerField(default=0)
    requisitos = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nivel', 'tipo']
        verbose_name = 'Insignia'
        verbose_name_plural = 'Insignias'
    
    def __str__(self):
        return f"🏅 {self.nombre} ({self.get_nivel_display()})"


class InsigniaUsuario(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='insignias')
    insignia = models.ForeignKey('Insignia', on_delete=models.CASCADE, related_name='usuarios')
    fecha_obtenida = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)
    progreso = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['usuario', 'insignia']
        ordering = ['-fecha_obtenida']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.insignia.nombre}"


class PuntajeUsuario(models.Model):
    NIVELES_USUARIO = [
        ('BRONCE', 'Bronce'),
        ('PLATA', 'Plata'),
        ('ORO', 'Oro'),
        ('DIAMANTE', 'Diamante'),
        ('EXPERTO', 'Experto'),
    ]
    
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='puntaje')
    puntos_totales = models.IntegerField(default=0)
    puntos_curso = models.JSONField(default=dict, blank=True)
    ejercicios_resueltos = models.IntegerField(default=0)
    ejercicios_correctos = models.IntegerField(default=0)
    racha_actual = models.IntegerField(default=0)
    racha_maxima = models.IntegerField(default=0)
    ultimo_ejercicio = models.DateTimeField(null=True, blank=True)
    nivel_general = models.CharField(max_length=20, choices=NIVELES_USUARIO, default='BRONCE')
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-puntos_totales']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.puntos_totales} pts - {self.nivel_general}"
    
    @property
    def porcentaje_precision(self):
        if self.ejercicios_resueltos == 0:
            return 0
        return round((self.ejercicios_correctos / self.ejercicios_resueltos) * 100, 1)


class ComentarioEntrega(models.Model):
    entrega = models.ForeignKey('EntregaArchivo', on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class PerfilUsuario(models.Model):
    """Modelo para gestionar roles y perfiles de usuarios"""
    ROLES = [
        ('SUPERUSUARIO', 'Superusuario'),
        ('PROFESOR', 'Profesor'),
        ('ESTUDIANTE', 'Estudiante'),
        ('ADMIN', 'Administrador'),
    ]
    
    usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='ESTUDIANTE')
    identificacion = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    biografia = models.TextField(blank=True, null=True)
    redes_sociales = models.JSONField(default=dict, blank=True)
    cursos_inscritos = models.ManyToManyField('Curso', related_name='estudiantes_inscritos', blank=True)
    cursos_impartidos = models.ManyToManyField('Curso', related_name='profesores', blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"
    
    @property
    def es_superusuario(self):
        return self.rol == 'SUPERUSUARIO' or self.usuario.is_superuser
    
    @property
    def es_profesor(self):
        return self.rol == 'PROFESOR' or self.usuario.is_staff
    
    @property
    def es_estudiante(self):
        return self.rol == 'ESTUDIANTE'
    
    @property
    def nombre_completo(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}".strip() or self.usuario.username

class Mensaje(models.Model):
    """Modelo para mensajería entre usuarios"""
    TIPOS = [
        ('PRIVADO', 'Privado'),
        ('GRUPO', 'Grupo'),
        ('SISTEMA', 'Sistema'),
    ]
    
    ESTADOS = [
        ('ENVIADO', 'Enviado'),
        ('LEIDO', 'Leído'),
        ('RESPONDIDO', 'Respondido'),
        ('ARCHIVADO', 'Archivado'),
    ]
    
    remitente = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='mensajes_recibidos', null=True, blank=True)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, null=True, blank=True, related_name='mensajes')
    
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='PRIVADO')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ENVIADO')
    
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_leido = models.DateTimeField(null=True, blank=True)
    
    adjuntos = models.ManyToManyField('EntregaArchivo', blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['remitente']),
            models.Index(fields=['destinatario']),
            models.Index(fields=['curso']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.remitente.username} -> {self.destinatario.username if self.destinatario else 'Grupo'}: {self.asunto[:30]}"
    
    def marcar_como_leido(self):
        self.estado = 'LEIDO'
        self.fecha_leido = datetime.now()
        self.save()
    
    @property
    def es_leido(self):
        return self.estado == 'LEIDO'
    
    @property
    def tiempo_envio(self):
        from django.utils import timezone
        delta = timezone.now() - self.fecha_envio
        if delta.days > 0:
            return f"{delta.days} días"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} horas"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutos"
        else:
            return "hace un momento"

class Notificacion(models.Model):
    """Modelo para notificaciones del sistema"""
    TIPOS = [
        ('MENSAJE', 'Nuevo mensaje'),
        ('CURSO', 'Curso asignado'),
        ('EVALUACION', 'Evaluación disponible'),
        ('CERTIFICADO', 'Certificado obtenido'),
        ('SISTEMA', 'Notificación del sistema'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='SISTEMA')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    url = models.CharField(max_length=500, blank=True, null=True)
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo[:30]}"
    
    def marcar_como_leido(self):
        self.leido = True
        self.save()
