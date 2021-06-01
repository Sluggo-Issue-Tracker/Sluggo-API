from django.db import models
from .team import Team
from django.conf import settings
import uuid


class Event(models.Model):
    CREATE = 1
    UPDATE = 2
    DELETE = 3

    events = [
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete"),
    ]

    created = models.DateTimeField(auto_now_add=True)
    event_type = models.SmallIntegerField(choices=events)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL)
    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             editable=True,
                             null=False,
                             related_name="event")
    object = models.UUIDField(null=False, blank=False)

    class Meta:
        ordering = ["-created"]
        app_label = "api"

    def is_create(self):
        return self.CREATE == self.event_type

    def is_update(self):
        return self.UPDATE == self.event_type

    def is_delete(self):
        return self.DELETE == self.event_type

    def __str__(self):
        return f"Event: {self.event_type}, {self.description} for Team: {self.team.name}"
