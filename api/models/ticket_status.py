from django.db import models
from .team import Team
from hashlib import md5

from api.models.interfaces import HasUuid, TeamRelated


class TicketStatus(HasUuid, TeamRelated):
    """
    This model represents custom statuses that teams can set.
    By default, they will be created, started, and completed
    """

    team_title_hash = models.CharField(max_length=256,
                                       unique=True,
                                       editable=False)
    title = models.CharField(max_length=100, unique=False)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"TicketStatus: {self.title}"

    def save(self, *args, **kwargs):
        team = self.team
        title = self.title

        if not title:
            raise ValueError("missing title")

        if not team:
            raise ValueError("missing team")

        title_id = "{}".format(title)
        team_id = "{}".format(team.id)
        self.team_title_hash = md5(title_id.encode()).hexdigest() + md5(
            team_id.encode()).hexdigest()

        super(TicketStatus, self).save(*args, **kwargs)
