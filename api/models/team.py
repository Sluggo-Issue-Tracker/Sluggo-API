from django.db import models


class Team(models.Model):
    """
    this represents a team in sluggo
    """

    # md5(name)
    id = models.BinaryField(max_length=128, unique=True, blank=False, primary_key=True)
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField()
    ticket_head = models.IntegerField(blank=False, default=0)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Team: {self.name}"
