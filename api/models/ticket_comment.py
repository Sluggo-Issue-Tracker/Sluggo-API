from django.db import models
from django.conf import settings

from .ticket import Ticket
from .team import Team
from api.models.interfaces import HasUuid
import uuid


class TicketComment(HasUuid):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        editable=True,
        null=False,
        related_name="ticket_comment",
    )

    class Meta:
        app_label = "api"

    def __str__(self):
        return f"Comment: {self.content} for Team: {self.team.name}"
