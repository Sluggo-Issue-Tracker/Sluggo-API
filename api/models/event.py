from django.db import models
from .team import Team
from django.conf import settings

class Event(models.Model):
    CREATE = 1
    UPDATE = 2
    DELETE = 3

    events = [
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete"),
    ]

    team = models.ForeignKey(Team, on_delete=models.SET_NULL)
    edited = models.DateTimeField(auto_now_add=True)
    event_type = models.SmallIntegerField(choices=events)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    object = models.UUIDField()

    def is_create(self):
        return self.CREATE == self.event_type
    def is_update(self):
        return self.UPDATE == self.event_type
    def is_delete(self):
        return self.DELETE == self.event_type

    class Meta:
        ordering = ["-edited"]
        app_label = "api"