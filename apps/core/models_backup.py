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

class Evaluacion(models.Model):
    TIPOS = [
        ('QUIZ', 'Quiz'),
        ('EXAMEN', 'Examen'),
        ('PRACTICA', 'Práctica'),
        ('PROYECTO', 'Proyecto'),
    ]
    
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='evaluaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='QUIZ')
    lecciones = models.ManyToManyField('Lesson', blank=True, related_name='evaluaciones')
    preguntas = models.JSONField(default=list, blank=True)
    puntaje_maximo = models.IntegerField(default=100)
    duracion_minutos = models.IntegerField(default=30)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.titulo} ({self.curso.titulo[:30]})"

class Pregunta(models.Model):
    TIPOS = [
        ('OPCION_MULTIPLE', 'Opción Múltiple'),
        ('VERDADERO_FALSO', 'Verdadero/Falso'),
        ('TEXTO', 'Respuesta Texto'),
        ('NUMERICA', 'Respuesta Numérica'),
    ]
    
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE, related_name='preguntas')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='OPCION_MULTIPLE')
    texto = models.TextField()
    opciones = models.JSONField(default=list, blank=True)
    respuesta_correcta = models.TextField()
    puntaje = models.IntegerField(default=5)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.texto[:50]}..."

class PracticaPrevia(models.Model):
    """
    Modelo para prácticas previas (pre-tests) antes de las lecciones
    """
    TIPOS = [
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('PRE_TEST', 'Pre-Test'),
        ('REPASO', 'Repaso'),
        ('PREPARACION', 'Preparación'),
    ]
    
    leccion = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='practicas_previas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='PRE_TEST')
    preguntas = models.JSONField(default=list, blank=True)
    puntaje_maximo = models.IntegerField(default=100)
    duracion_minutos = models.IntegerField(default=15)
    es_obligatoria = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['leccion', 'fecha_creacion']
        verbose_name = 'Práctica Previa'
        verbose_name_plural = 'Prácticas Previas'
    
    def __str__(self):
        return f"{self.titulo} - {self.leccion.titulo[:30]}"

class RespuestaPractica(models.Model):
    """
    Modelo para respuestas de prácticas previas
    """
    practica_previa = models.ForeignKey('PracticaPrevia', on_delete=models.CASCADE, related_name='respuestas')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='respuestas_practicas', null=True, blank=True)
    respuestas = models.JSONField(default=dict)
    puntaje_obtenido = models.IntegerField(default=0)
    porcentaje = models.FloatField(default=0.0)
    tiempo_invertido = models.IntegerField(default=0)  # en segundos
    fecha_realizacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_realizacion']
        verbose_name = 'Respuesta de Práctica'
        verbose_name_plural = 'Respuestas de Prácticas'
    
    def __str__(self):
        return f"{self.practica_previa.titulo} - {self.usuario or 'Anónimo'}"

class Certificado(models.Model):
    """
    Modelo para certificados de finalización de cursos
    """
    TIPOS = [
        ('CURSO', 'Curso Completo'),
        ('MODULO', 'Módulo Completado'),
        ('EVALUACION', 'Evaluación Aprobada'),
        ('PRACTICA', 'Práctica Completada'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('GENERADO', 'Generado'),
        ('ENTREGADO', 'Entregado'),
        ('REVOCADO', 'Revocado'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='certificados', null=True, blank=True)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='certificados')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='CURSO')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Datos del certificado
    nombre_completo = models.CharField(max_length=200)
    identificacion = models.CharField(max_length=50, blank=True, null=True)
    puntaje_obtenido = models.FloatField(default=0.0)
    porcentaje = models.FloatField(default=0.0)
    
    # Fechas
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    codigo_verificacion = models.CharField(max_length=100, unique=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    habilidades = models.JSONField(default=list, blank=True)
    
    # Archivo
    archivo_pdf = models.FileField(upload_to='certificados/', null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_completado', '-fecha_creacion']
        unique_together = ['usuario', 'curso', 'tipo']
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
    
    def save(self, *args, **kwargs):
        if not self.codigo_verificacion:
            import hashlib
            import time
            # Generar código único de verificación
            raw = f"{self.usuario_id or 'anon'}-{self.curso_id}-{time.time()}"
            self.codigo_verificacion = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Certificado: {self.nombre_completo} - {self.curso.titulo[:30]}"
    
    @property
    def esta_completado(self):
        return self.estado in ['GENERADO', 'ENTREGADO']
    
    @property
    def esta_pendiente(self):
        return self.estado == 'PENDIENTE'

class Logro(models.Model):
    """
    Modelo para logros y badges que se pueden obtener
    """
    TIPOS = [
        ('CURSO', 'Curso Completado'),
        ('EVALUACION', 'Evaluación Aprobada'),
        ('PRACTICA', 'Práctica Completada'),
        ('RACHA', 'Racha de Estudio'),
        ('PUNTUACION', 'Puntuación Alta'),
        ('ESPECIAL', 'Logro Especial'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    icono = models.CharField(max_length=50, default='fa-star')
    color = models.CharField(max_length=20, default='#FFD700')
    puntos = models.IntegerField(default=10)
    requisitos = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"🏆 {self.nombre} ({self.get_tipo_display()})"

class LogroUsuario(models.Model):
    """
    Modelo para asociar logros a usuarios
    """
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='logros')
    logro = models.ForeignKey('Logro', on_delete=models.CASCADE, related_name='usuarios')
    fecha_obtenido = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['usuario', 'logro']
        ordering = ['-fecha_obtenido']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.logro.nombre}"
