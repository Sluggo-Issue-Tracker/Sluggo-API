from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Team(models.Model):
    """
    this represents a team in sluggo
    """

    name = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(auto_now_add=True)
    deactivated =models.DateTimeField()

    def __str__(self):
        return f"Team: {self.title}"