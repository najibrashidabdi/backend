from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import QuizQuestion, Submission
from .serializers import QuizQuestionSerializer, SubmissionSerializer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@api_view(["GET"])
def get_questions(request):
    """
    Return all quiz questions in JSON format.
    """
    questions = QuizQuestion.objects.all()
    serializer = QuizQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def submit_quiz(request):
    """
    Receives a username, color, and list of question/answer pairs from the frontend.
    - Calculates how many were correct
    - Computes new points (4 points per correct answer)
    - Accumulates them into the user's existing score (or creates a new submission if none)
    - Broadcasts the updated leaderboard to all WebSocket clients
    - Returns the user's new total score and rank
    """
    data = request.data
    username = data.get("username")
    color = data.get("color", "")
    answers = data.get("answers", [])

    if not username or not answers:
        return Response({"detail": "Missing username or answers"}, status=status.HTTP_400_BAD_REQUEST)

    correct_count = 0
    total_questions = len(answers)
    points_per_question = 10  # Points per correct question

    # Count how many answers were correct
    for ans in answers:
        qid = ans.get("questionId")
        selected = ans.get("selectedAnswer")
        try:
            question = QuizQuestion.objects.get(id=qid)
            if question.correct_answer == selected:
                correct_count += 1
        except QuizQuestion.DoesNotExist:
            # If the question doesn't exist, optionally handle that scenario
            total_questions -= 1

    if total_questions <= 0:
        return Response({"detail": "No valid questions found."}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate new points for this submission attempt
    new_points = correct_count * points_per_question

    # Update or create a Submission for this user
    existing_submission = Submission.objects.filter(username=username).first()
    if existing_submission:
        existing_submission.score += new_points
        existing_submission.color = color
        existing_submission.save()
        submission = existing_submission
    else:
        submission = Submission.objects.create(
            username=username,
            color=color,
            score=new_points
        )

    # Calculate the user's rank (1-based)
    user_rank = Submission.objects.filter(score__gt=submission.score).count() + 1

    # Broadcast the updated leaderboard in real time
    channel_layer = get_channel_layer()
    subs = Submission.objects.all().order_by("-score", "submitted_at")[:10]
    leaderboard_data = SubmissionSerializer(subs, many=True).data
    async_to_sync(channel_layer.group_send)(
        "leaderboard",
        {
            "type": "leaderboard_update",
            "data": leaderboard_data
        }
    )

    # Return data about the quiz attempt
    return Response({
        "submission": SubmissionSerializer(submission).data,
        "correctAnswers": correct_count,
        "totalQuestions": total_questions,
        "newPoints": new_points,
        "updatedScore": submission.score,
        "rank": user_rank
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def leaderboard(request):
    """
    Return the top 10 submissions (score desc, tiebreak by submitted_at)
    """
    top_submissions = Submission.objects.all().order_by("-score", "submitted_at")[:10]
    serializer = SubmissionSerializer(top_submissions, many=True)
    return Response(serializer.data)
