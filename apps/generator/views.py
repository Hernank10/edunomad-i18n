from django.shortcuts import render, get_object_or_404
from .models import GeneratedExercise
import random

def random_exercise(request):
    # Obtenemos todos los IDs disponibles
    exercise_ids = GeneratedExercise.objects.values_list('id', flat=True)
    if not exercise_ids:
        return render(request, 'generator/no_exercises.html')
    
    # Elegimos uno al azar
    random_id = random.choice(exercise_ids)
    exercise = get_object_or_404(GeneratedExercise, id=random_id)
    
    # Simulación de progreso (ejemplo: 15 de 50)
    total = len(exercise_ids)
    current_count = 15 
    progress_percentage = (current_count / total) * 100

    return render(request, 'generator/exercise_detail.html', {
        'exercise': exercise,
        'progress': progress_percentage,
        'current_count': current_count,
        'total': total
    })
