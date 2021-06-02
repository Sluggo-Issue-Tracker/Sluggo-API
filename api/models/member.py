from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from hashlib import md5
from ..methods import hash_team_id

from api.models.interfaces import HasUuid
from .team import Team
from .team_invite import TeamInvite

User = get_user_model()


class Member(HasUuid):
    class Roles(models.TextChoices):
        APPROVED = "AP", _("Approved")
        ADMIN = "AD", _("Admin")

    # team.team_id + md5 (user.username)
    # TODO: this should probably migrate just to a normal id
    id = models.CharField(max_length=256,
                          unique=True,
                          editable=False,
                          primary_key=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              editable=True)

    role = models.CharField(max_length=2,
                            choices=Roles.choices,
                            default=Roles.APPROVED)

    pronouns = models.CharField(max_length=256, null=True, blank=True)

    bio = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)

    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             editable=True,
                             null=False,
                             related_name="member")

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_approved(self):
        return self.role == self.Roles.ADMIN or self.role == self.Roles.APPROVED

    @classmethod
    def get_member(cls, user, team: Team):
        team_id = team.id
        team_id = "{}".format(team_id)
        username = user.username
        member_pk = (md5(team_id.encode()).hexdigest() +
                     md5(username.encode()).hexdigest())
        return Member.objects.get(pk=member_pk)

    class Meta:
        ordering = ["created"]
        app_label = "api"
        unique_together = [["owner", "team"]]

    def __str__(self):
        return f"Member: {self.owner.username} for Team: {self.team.name}"

    def _pre_create(self):
        team: Team = self.team
        owner: User = self.owner

        self.id = hash_team_id(team, owner.username)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(Member, self).save(*args, **kwargs)
