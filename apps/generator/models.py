from django.db import models

class GrammarRule(models.Model):
    name = models.CharField(max_length=100)
    pattern = models.JSONField(help_text="Subjects, Verbs, Objects")
    language = models.CharField(max_length=50, default='Español')

class GeneratedExercise(models.Model):
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
