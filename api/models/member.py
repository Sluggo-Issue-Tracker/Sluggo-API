from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from . import Team

class Member(models.Model):
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
    class Roles(models.TextChoices):
        """
        A private class containing 3 options for Roles stored in multiple versions. A full name, "pretty" name, and 2-letter representation.

        The options are:
            Unapproved: Roles.UNAPPROVED, Roles['UNAPPROVED'] or Roles('UA')
            Approved: Roles.APPROVED, Roles['APPROVED'] or Roles('AP')
            Admin: Roles.ADMIN, Roles['ADMIN'] or Roles('AD')
        """

        UNAPPROVED = "UA", _("Unapproved")
        APPROVED = "AP", _("Approved")
        ADMIN = "AD", _("Admin")

    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    team_id = models.ForeignKey(
        Team, on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=2, choices=Roles.choices, default=Roles.UNAPPROVED
    )

    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Member: {self.title}"

    # when the AUTH_USER_MODEL saves, update roles to admin if they are a supervisor or are staff
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_member(sender, instance, created, **kwargs):
        if created:
            if instance.is_superuser or instance.is_staff:
                Member.objects.create(owner=instance, role=Member.Roles.ADMIN)
            else:
                Member.objects.create(owner=instance)
