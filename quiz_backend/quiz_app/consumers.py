import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Max
from asgiref.sync import sync_to_async
from .models import Submission
from .serializers import SubmissionSerializer

class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the leaderboard group
        await self.channel_layer.group_add("leaderboard", self.channel_name)
        await self.accept()

        # Send current leaderboard immediately on connect
        data = await self.get_leaderboard_data()
        await self.send(json.dumps({"type": "leaderboard", "data": data}))

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard("leaderboard", self.channel_name)

    async def receive(self, text_data):
        # Typically we don't receive messages from the client in this example
        pass

    async def leaderboard_update(self, event):
        # This is called whenever your view does group_send(...)
        data = event["data"]
        await self.send(json.dumps({"type": "leaderboard", "data": data}))

    @sync_to_async
    def get_leaderboard_data(self):
        submissions = Submission.objects.all().order_by("-score", "submitted_at")[:10]
        serializer = SubmissionSerializer(submissions, many=True)
        return serializer.data
