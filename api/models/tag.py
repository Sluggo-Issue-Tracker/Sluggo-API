from django.db import models
import uuid
from .team import Team
from .ticket import Ticket
from api.models.interfaces import HasUuid
from hashlib import md5
import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from ..methods import hash_team_id


class Tag(HasUuid):
    team_title_hash = models.CharField(max_length=256, unique=True, editable=False)
    title = models.CharField(
        max_length=100,
        unique=False,
        validators=[
            RegexValidator(
                re.compile(r"^[\w-]+$"),
                _("Tag names must be word characters and dashes"),
                "invalid",
            )
        ],
    )
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, editable=True, null=False, related_name="tag"
    )

    class Meta:
        ordering = ["id"]
        unique_together = [["title", "team"]]
        app_label = "api"

    def __str__(self):
        return f"Tag: {self.title} for Team: {self.team.name}"

    def _pre_create(self):
        team = self.team
        title = self.title

        self.team_title_hash = hash_team_id(team, title)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(Tag, self).save(*args, **kwargs)
