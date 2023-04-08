import uuid
from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone


class Node(models.Model):
    class Meta:
        abstract = True
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)


class Thing(Node):
    class Meta:
        abstract = True
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name if self.name else str(self.id)


class Video(Thing):
    rating = models.FloatField(default=0.0)


class Stream(Node):
    node_type = models.CharField(max_length=255)
    node_id = models.UUIDField()
    qty = models.IntegerField()
    streamed = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)