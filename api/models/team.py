from django.db import models
from hashlib import md5

class Team(models.Model):

    # id is implicitly defined by django
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField()
    ticket_head = models.IntegerField(blank=False, default=0, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    teamUUID = models.UUIDField(null=True, blank=False)

    class Meta:
        ordering = ["created"]
        app_label = "api"

    def __str__(self):
        return f"Team: {self.id}, {self.name}"
