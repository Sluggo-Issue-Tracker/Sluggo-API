from django.db import models
from django.conf import settings

from .member import Member
from .team import Team
from .ticket_status import TicketStatus
from api.models.interfaces import HasUuid


class Ticket(HasUuid):
    ticket_number = models.IntegerField()

    assigned_user = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        related_name="assigned_ticket",
        null=True,
        blank=True,
    )

    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.SET_NULL,
        related_name="status_ticket",
        blank=True,
        null=True,
    )

    members_pins = models.ManyToManyField("Member", through="PinnedTicket")
    tag_list = models.ManyToManyField("Tag", through="TicketTag")
    due_date = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, editable=True, null=False, related_name="ticket"
    )

    class Meta:
        ordering = ["id"]
        app_label = "api"

    @classmethod
    def retrieve_by_user(cls, user: settings.AUTH_USER_MODEL, team: Team):
        return cls.objects.filter(
            models.Q(team=team),
            models.Q(deactivated=None),
            models.Q(assigned_user=user),
        )

    def __str__(self):
        return f"Ticket: {self.title} for Team: {self.team.name}"

    def _pre_create(self):
        team = self.team

        team.ticket_head += 1
        team.save()
        self.ticket_number = team.ticket_head

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(Ticket, self).save(*args, **kwargs)
