from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from .team import Team
from .ticket_status import TicketStatus
from ..methods import hash_team_id
from api.models.interfaces import HasUuid

User = get_user_model()


class TeamInvite(HasUuid):
    team_user_hash = models.CharField(max_length=256,
                                      unique=True,
                                      editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             editable=True)

    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             editable=True,
                             null=False,
                             related_name="member")

    def _pre_create(self):
        team: Team = self.team
        user: User = self.user

        self.team_user_hash = hash_team_id(team, user.username)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()
        super().save(*args, **kwargs)
