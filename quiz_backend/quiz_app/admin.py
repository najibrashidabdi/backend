from django.contrib import admin
from .models import QuizQuestion, Submission

admin.site.register(QuizQuestion)
admin.site.register(Submission)