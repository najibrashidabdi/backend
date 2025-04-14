from django.db import models

class QuizQuestion(models.Model):
    question_text = models.TextField()
    options = models.JSONField(default=list)  # store multiple choices
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text[:50]


class Submission(models.Model):
    username = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    # Optionally track total time spent or similar exam data if you like

    def __str__(self):
        return f"{self.username} - {self.score}"
