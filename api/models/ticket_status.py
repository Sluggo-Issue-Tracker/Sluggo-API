from django.db import models
from .team import Team


class TicketStatus(models.Model):
    """
    This model represents custom statuses that teams can set.
    By default, they will be created, started, and completed
    """

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    ticket_statusUUID = models.UUIDField(null=True, blank=False)

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"TicketStatus: {self.title}"
