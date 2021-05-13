from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .team import Team
from hashlib import md5
import re

from api.models.interfaces import HasUuid

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .fields.color_field import ColorField


class TicketStatus(HasUuid, models.Model):
    team_title_hash = models.CharField(max_length=256,
                                       unique=True,
                                       editable=False)

    title = models.CharField(max_length=100,
                             unique=False)

    color = ColorField(unique=False,
                       blank=True, default="#B9B9BDFF")
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             editable=True,
                             null=False,
                             related_name="ticket_status")

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"TicketStatus: {self.title}"

    def _pre_create(self):
        team = self.team
        title = self.title

        title_id = "{}".format(title)
        team_id = "{}".format(team.id)
        self.team_title_hash = md5(title_id.encode()).hexdigest() + md5(
            team_id.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(TicketStatus, self).save(*args, **kwargs)


@receiver(post_save, sender=Team)
def create_team_defaults(sender, instance: Team, created: bool, **kwargs):
    if created:
        TicketStatus.objects.create(title="To do", color="#3273DCFF", team=instance)
        TicketStatus.objects.create(title="In Progress", color="#FFDD57", team=instance)
        TicketStatus.objects.create(title="Done", color="#48C774FF", team=instance)
