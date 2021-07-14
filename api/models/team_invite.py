from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from .team import Team
from .ticket_status import TicketStatus
from ..methods import hash_team_id
from api.models.interfaces import HasUuid

User = get_user_model()


class TeamInvite(HasUuid):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=True
    )

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, editable=True, null=False, related_name="invite"
    )

    class Meta:
        ordering = ["id"]
        app_label = "api"
        unique_together = [["user", "team"]]
