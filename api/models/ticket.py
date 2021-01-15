from django.db import models
from django.conf import settings

from .team import Team
from .ticket_status import TicketStatus
from .member import Member
from .has_uuid import HasUuid
import uuid


class TicketManager(models.Manager):
    # this is a convenience class which handles defining the id before a save
    # ( i think it gets automatically invoked on member instantiation before save)
    def create(self, **obj_data):
        team = obj_data.get("team")
        owner = obj_data.get('owner')

        if not owner or not team:
            raise ValueError("missing name or team")

        ticketUUID = uuid.uuid4()
        team.ticket_head += 1
        team.save()
        obj_data["ticket_number"] = team.ticket_head

        return super().create(**obj_data)


class Ticket(HasUuid):
    """
    The Ticket class for Sluggo. This will store all information associated with a specific ticket.

    The class contains:
        owner: A foreign key to a specific user that authored the ticket. Allows for them to edit the ticket.
        assigned_user: A foreign key that refers to a specific user that the ticket is assigned to.
        title: A char field for the title of the ticket (currently limited to 100 characters and is a required field).
        description: A multiline text field that will store the longer form explanation of the ticket.
        created: A datetime field that will record when a ticket has been made.
        started: A ticket can be made before anyone actually starts it, so the started field must be seperate. (Also datetime)
        completed: A field to record when a ticket has been finished. (Datetime as well)
        due_date: The due date for the ticket, a date field that will keep track of when things are due.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    ticket_number = models.IntegerField()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_ticket"
    )

    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_ticket",
        null=True,
        blank=True
    )

    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.CASCADE,
        related_name="status_ticket",
        blank=True,
        null=True
    )

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    ticketUUID = models.UUIDField(null=True, blank=False, default=uuid.uuid4, editable=False, unique=True)

    objects = TicketManager()

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"Ticket: {self.title}"
