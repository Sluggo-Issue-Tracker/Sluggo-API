from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from hashlib import md5

from .team import Team


class MemberManager(models.Manager):
    # this is a convenience class which handles defining the id before a save
    # ( i think it gets automatically invoked on member instantiation before save)
    def create(self, **obj_data):
        team = obj_data.get("team")
        user = obj_data.get("user")

        if not user or not team:
            raise ValueError("missing name or team")

        # id will be an md5 of the team.id formatted as a string, followed by the md5 of the username

        obj_data["id"] = md5("f{team.id}".encode()).hexdigest() + md5(user.username.encode()).hexdigest()
        return super().create(**obj_data)


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
        # TODO: Samuel Schmidt 10/13/2020 this needs to be refactored its own table,
        # i think having custom roles is a feature we want to implement
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

    # team.team_id + md5 (user.username)
    id = models.CharField(max_length=256, unique=True, editable=False, primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False
    )

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, editable=False
    )

    role = models.CharField(
        max_length=2, choices=Roles.choices, default=Roles.UNAPPROVED
    )

    bio = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    objects = MemberManager()

    class Meta:
        ordering = ["created"]
        app_label = "api"

    def __str__(self):
        return f"Member: {self.user.get_full_name}"
