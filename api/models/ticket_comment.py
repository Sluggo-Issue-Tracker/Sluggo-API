from django.db import models
from django.conf import settings

from .ticket import Ticket
from .team import Team
from api.models.interfaces import HasUuid, TeamRelated
import uuid


class TicketComment(HasUuid, TeamRelated):
    """
    Comment object for tickets
    """

    ticket = models.ForeignKey(
        Ticket,
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

    class Meta:
        app_label = "api"

    def __str__(self):
        return f"Comment: {self.content}"
