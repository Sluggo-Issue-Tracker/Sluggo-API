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
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    ticket_commentUUID = models.UUIDField()

    class Meta:
       app_label = "api"

    def __str__(self):
        return f"Comment: {self.content}"
