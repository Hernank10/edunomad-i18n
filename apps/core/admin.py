from django.contrib import admin
from .models import RecursoEducativo, Curso

@admin.register(RecursoEducativo)
class RecursoEducativoAdmin(admin.ModelAdmin):
    list_display = ['nombre_archivo', 'categoria', 'extension', 'tamanio_kb']
    list_filter = ['categoria', 'extension']
    search_fields = ['nombre_archivo', 'categoria', 'descripcion']
    
    def tamanio_kb(self, obj):
        return f"{obj.tamanio_kb:.2f} KB"
    tamanio_kb.short_description = 'Tamaño (KB)'

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'nivel', 'estado', 'duracion_horas', 'total_recursos']
    list_filter = ['categoria', 'nivel', 'estado']
    search_fields = ['titulo', 'descripcion', 'palabras_clave']
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ['recursos']
    
    def total_recursos(self, obj):
        return obj.recursos.count()
    total_recursos.short_description = '# Recursos'

from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'nombre_completo', 'identificacion', 'fecha_registro']
    list_filter = ['rol', 'is_active']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'identificacion']
    readonly_fields = ['fecha_registro', 'ultimo_acceso']
    
    fieldsets = (
        ('Datos Personales', {
            'fields': ('usuario', 'rol', 'identificacion', 'telefono', 'direccion', 'fecha_nacimiento')
        }),
        ('Información Adicional', {
            'fields': ('biografia', 'redes_sociales', 'foto')
        }),
        ('Cursos', {
            'fields': ('cursos_inscritos', 'cursos_impartidos')
        }),
        ('Estado', {
            'fields': ('is_active', 'fecha_registro', 'ultimo_acceso')
        }),
    )
    
    def nombre_completo(self, obj):
        return obj.nombre_completo
    nombre_completo.short_description = 'Nombre Completo'
