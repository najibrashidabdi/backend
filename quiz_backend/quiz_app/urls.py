from django.urls import path
from django.urls import path
from .views import get_questions, submit_quiz, leaderboard

urlpatterns = [
    path('questions/', get_questions, name='get_questions'),
    path('submit/', submit_quiz, name='submit_quiz'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
