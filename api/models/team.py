from django.db import models
from hashlib import md5


class TeamManager(models.Manager):
    def create(self, **obj_data):
        name = obj_data.get("name")

        if not name:
            raise ValueError("missing name")

        team_id = md5(name.encode()).hexdigest()
        obj_data["id"] = team_id
        return super().create(**obj_data)


class Team(models.Model):
    """
    this represents a team in sluggo
    """

    # md5(name)
    id = models.CharField(max_length=128, unique=True, blank=False, primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField()
    ticket_head = models.IntegerField(blank=False, default=0, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    objects = TeamManager()

    class Meta:
        ordering = ["created"]
        app_label = "api"

    def __str__(self):
        return f"Team: {self.id}, {self.name}"
