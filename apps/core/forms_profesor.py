# -*- coding: utf-8 -*-
"""Formularios para el panel del profesor."""
from django import forms
from apps.core.models import Curso, Practica, Evaluacion
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
