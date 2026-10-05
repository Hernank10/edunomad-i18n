from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=50, default="Español")
    level = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.level})"

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
