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
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"TicketStatus: {self.title}"
