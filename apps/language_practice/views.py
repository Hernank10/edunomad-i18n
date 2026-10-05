from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson
from apps.generator.models import GeneratedExercise

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'language_practice/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    return render(request, 'language_practice/course_detail.html', {
        'course': course, 
        'lessons': lessons
    })
