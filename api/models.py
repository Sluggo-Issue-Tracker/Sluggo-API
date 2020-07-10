from django.db import models
from django.contrib.auth.models import User
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
        User, on_delete=models.CASCADE, related_name="profiles"
    )
    role = models.CharField(
        max_length=2, choices=Roles.choices, default=Roles.UNAPPROVED
    )
    bio = models.TextField()

    class Meta:
        ordering = ["id"]

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
        User, related_name="created_tickets", on_delete=models.CASCADE
    )
    assigned_user = models.ForeignKey(
        User, related_name="assigned_tickets", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["id"]


# REST TUTORIAL BELOW HERE #

# Imports for REST Tutorial
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default="")
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, default="python", max_length=100
    )
    style = models.CharField(choices=STYLE_CHOICES, default="friendly", max_length=100)
    owner = models.ForeignKey(User, related_name="snippets", on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ["created"]

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = "table" if self.linenos else False
        options = {"title": self.title} if self.title else {}
        formatter = HtmlFormatter(
            style=self.style, linenos=linenos, full=True, **options
        )
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)

