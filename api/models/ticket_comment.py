from django.db import models
from django.conf import settings

from .ticket import Ticket
from .team import Team


class TicketComment(models.Model):
    """
    Comment object for tickets
    """

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(blank=True)

    def __str__(self):
        return f"Comment: {self.content}"
