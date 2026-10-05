# -*- coding: utf-8 -*-
"""Formularios para el panel del profesor."""
from django import forms
from apps.core.models import Curso, Practica, Evaluacion, EjercicioInteractivo
from apps.language_practice.models import Lesson


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = [
            "titulo", "descripcion", "categoria", "nivel", "estado",
            "duracion_horas", "precio", "palabras_clave", "imagen_url",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "categoria": forms.TextInput(attrs={"class": "form-control"}),
            "nivel": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "duracion_horas": forms.NumberInput(attrs={"class": "form-control"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "palabras_clave": forms.TextInput(attrs={"class": "form-control"}),
            "imagen_url": forms.URLInput(attrs={"class": "form-control"}),
        }


class LeccionForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class PracticaForm(forms.ModelForm):
    class Meta:
        model = Practica
        fields = ["titulo", "descripcion", "tipo", "puntaje_maximo",
                  "duracion_minutos", "orden", "is_active"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "puntaje_maximo": forms.NumberInput(attrs={"class": "form-control"}),
            "duracion_minutos": forms.NumberInput(attrs={"class": "form-control"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ["titulo", "descripcion", "tipo", "puntaje_maximo",
                  "duracion_minutos", "nota_minima", "is_active"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "puntaje_maximo": forms.NumberInput(attrs={"class": "form-control"}),
            "duracion_minutos": forms.NumberInput(attrs={"class": "form-control"}),
            "nota_minima": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EjercicioInteractivoForm(forms.ModelForm):
    opciones_texto = forms.CharField(
        label="Opciones (una por linea)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )

    class Meta:
        model = EjercicioInteractivo
        fields = ["tipo", "pregunta", "respuesta_correcta",
                  "explicacion", "puntaje", "orden", "is_active"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "pregunta": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "respuesta_correcta": forms.TextInput(attrs={"class": "form-control"}),
            "explicacion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "puntaje": forms.NumberInput(attrs={"class": "form-control"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = getattr(self, "instance", None)
        if inst and inst.pk and inst.opciones:
            self.fields["opciones_texto"].initial = "\n".join(str(o) for o in inst.opciones)

    def clean_opciones_texto(self):
        txt = self.cleaned_data.get("opciones_texto") or ""
        return [l.strip() for l in txt.splitlines() if l.strip()]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.opciones = self.cleaned_data.get("opciones_texto", [])
        if commit:
            obj.save()
        return obj