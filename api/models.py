from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):

    """
    The Profile class for the users of Sluggo. This will store the necessary information as a wrapper table around User.

    The class contains:
        user: The one-to-one field that refers to a specific User
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=2, choices=Roles.choices, default=Roles.UNAPPROVED
    )
    bio = models.TextField()
    # icon = models.ImageField(default="default.jpg", upload_to="profile_pics") NEEDS PILLOW


# REST TUTORIAL BELOW HERE #

# Imports for REST Tutorial
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_styles() if item[1]]
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

    class Meta:
        ordering = ["created"]

