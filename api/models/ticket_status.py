from django.db import models
from .team import Team
from hashlib import md5
import re

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
    color = models.CharField(max_length=7, unique=False, blank=True, default="#B9B9BD")
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"TicketStatus: {self.title}"

    def _pre_create(self):
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

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        color = self.color
        valid = self.check_color(color)
        if not valid:
            raise ValueError("invalid color hex code")

        super(TicketStatus, self).save(*args, **kwargs)

    def check_color(self, color):
        match = re.match(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
        if match:
            return True
        else:
            return False
