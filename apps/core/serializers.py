from rest_framework import serializers
from .models import RecursoEducativo, Curso

class RecursoEducativoSerializer(serializers.ModelSerializer):
    tamanio_kb = serializers.SerializerMethodField()
    tamanio_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = RecursoEducativo
        fields = [
            'id', 'nombre_archivo', 'ruta_completa', 'extension', 
            'categoria', 'tipo_contenido', 'tamanio_bytes', 'tamanio_kb', 
            'tamanio_mb', 'fecha_creacion', 'fecha_modificacion', 
            'descripcion', 'etiquetas', 'importado_el'
        ]
    
    def get_tamanio_kb(self, obj):
        return obj.tamanio_kb
    
    def get_tamanio_mb(self, obj):
        return obj.tamanio_mb

class RecursoEducativoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoEducativo
        fields = ['id', 'nombre_archivo', 'categoria', 'extension']

class CursoSerializer(serializers.ModelSerializer):
    recursos = RecursoEducativoSimpleSerializer(many=True, read_only=True)
    total_recursos = serializers.IntegerField(read_only=True)
    tamanio_total_mb = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Curso
        fields = [
            'id', 'titulo', 'slug', 'descripcion', 'categoria', 
            'nivel', 'estado', 'duracion_horas', 'recursos', 
            'total_recursos', 'tamanio_total_mb', 'fecha_creacion',
            'fecha_actualizacion', 'palabras_clave', 'precio', 'imagen_url'
        ]

class CursoSimpleSerializer(serializers.ModelSerializer):
    total_recursos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Curso
        fields = [
            'id', 'titulo', 'slug', 'categoria', 'nivel', 
            'estado', 'duracion_horas', 'total_recursos', 'precio'
        ]
