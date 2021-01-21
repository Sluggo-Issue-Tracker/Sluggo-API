# this here defines the ticket_tags
from django.db import models
from django.conf import settings
import uuid
from .team import Team
from .ticket import Ticket
from .has_uuid import HasUuid
from hashlib import md5


class Tag(HasUuid):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    tagUUID = models.UUIDField(null=True, blank=False, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["id"]
        app_label = "api"

    def __str__(self):
        return f"Tag: {self.title}"


class TicketTagManager(models.Manager):
    def create(self, **obj_data):
        tag = obj_data.get("tag")
        ticket = obj_data.get("ticket")

        if not tag or not ticket:
            raise ValueError("missing name or team")

        team_id = "{}".format(tag.id)
        ticket_id = "{}".format(ticket.id)
        obj_data["id"] = md5(team_id.encode()).hexdigest() + md5(ticket_id.encode()).hexdigest()
        return super().create(**obj_data)


class TicketTag(HasUuid):
    id = models.CharField(max_length=256, unique=True, editable=False, primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='tag_list')
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    objects = TicketTagManager()

    class Meta:
        ordering = ["created"]
        app_label = "api"

    def __str__(self):
        return f"TicketTag: {self.created}"
