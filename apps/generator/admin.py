from django.contrib import admin
from .models import GrammarRule, GeneratedExercise

@admin.register(GrammarRule)
class GrammarRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'language')

@admin.register(GeneratedExercise)
class GeneratedExerciseAdmin(admin.ModelAdmin):
    list_display = ('question', 'rule', 'created_at')
