from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from . import Team


class Ticket(models.Model):
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

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    ticket_number = models.IntegerField()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_tickets",
        on_delete=models.CASCADE,
    )

    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tickets",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=100, blank=False)
    # TODO 8 / 31 / 2020 Samuel Schmidt make this a compressed field once we confirm that shitaki mushrooms work
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Ticket: {self.title}"
