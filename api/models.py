from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):

    """
    The Profile class for the users of Sluggo. This will store the necessary information as a wrapper table around User.

    The class contains:
        owner: The one-to-one field that refers to a specific User
        role: A record storing whether a user is Approved, Unapproved, or an Admin. Takes use of the Roles Private Class
        bio: A text field that will store each users Bio for their profile
        icon: A field that will allow users to upload images for their profile pictures.
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

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles"
    )
    role = models.CharField(
        max_length=2, choices=Roles.choices, default=Roles.UNAPPROVED
    )
    bio = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Profile: {self.owner.get_full_name}"

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            if instance.is_superuser or instance.is_staff:
                Profile.objects.create(owner=instance, role=Profile.Roles.ADMIN)
            else:
                Profile.objects.create(owner=instance)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_user_profile(sender, instance, **kwargs):
        instance.profiles.save()

    # icon = models.ImageField(default="default.jpg", upload_to="profile_pics") NEEDS PILLOW


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
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Ticket: {self.title}"
