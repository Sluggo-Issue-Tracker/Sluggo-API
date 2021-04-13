from django.db import models
from django.conf import settings

from .member import Member
from .team import Team
from .ticket_status import TicketStatus
from api.models.interfaces import HasUuid, TeamRelated
import uuid


class Ticket(HasUuid, TeamRelated):
    """
    The Ticket class for Sluggo. This will store all information associated with a specific ticket.

    The class contains:
        owner: Foreign key to the creating user.
        assigned_user: Foreign key to an assigned user.
        title: Text field which is the title.
        team: inherited from TeamRelated, references a team
        status: foreign key to status object
        description: text field for a description
        created: creation datetime
        activated: activation date for the ticket
        deactivated: deactivation date for the ticket
    """

    ticket_number = models.IntegerField()

    assigned_user = models.ForeignKey(Member,
                                      on_delete=models.SET_NULL,
                                      related_name="assigned_ticket",
                                      null=True,
                                      blank=True)

    status = models.ForeignKey(TicketStatus,
                               on_delete=models.SET_NULL,
                               related_name="status_ticket",
                               blank=True,
                               null=True)

    tag_list = models.ManyToManyField('Tag', through='TicketTag')
    due_date = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        app_label = "api"

    @classmethod
    def retrieve_by_user(cls, user: settings.AUTH_USER_MODEL, team: Team):
        return cls.objects.filter(
            models.Q(team=team), models.Q(deactivated=None),
            models.Q(assigned_user=user))

    def __str__(self):
        return f"Ticket: {self.title}"

    def _pre_create(self):
        team = self.team

        team.ticket_head += 1
        team.save()
        self.ticket_number = team.ticket_head

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(Ticket, self).save(*args, **kwargs)