# this here defines the ticket_tags
from django.db import models
import uuid
from .team import Team
from .ticket import Ticket
from .tag import Tag
from api.models.interfaces import HasUuid
from hashlib import md5
import re


class TicketTag(HasUuid):
    id = models.CharField(max_length=256, unique=True, editable=False, primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    activated = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        editable=True,
        null=False,
        related_name="ticket_tag",
    )

    class Meta:
        ordering = ["created"]
        unique_together = [["tag", "ticket"]]
        app_label = "api"

    @classmethod
    def create_all(cls, tag_list: list, ticket: Ticket):
        if not tag_list:
            return

        for tag in tag_list:
            cls.objects.create(tag=tag, ticket=ticket, team=ticket.team)

    @classmethod
    def delete_difference(cls, tag_list: list, ticket_instance: Ticket):
        if tag_list:
            filters = models.Q(tag=tag_list[0])
            for tag in tag_list[1:]:
                filters |= models.Q(tag=tag)

            # select all that are not in the tag list
            to_be_deleted = cls.objects.filter(ticket=ticket_instance).exclude(filters)

            for tag in tag_list:
                cls.objects.get_or_create(
                    ticket=ticket_instance, tag=tag, team=ticket_instance.team
                )
        else:
            to_be_deleted = cls.objects.filter(ticket=ticket_instance)

        for ticket_tag in to_be_deleted:
            ticket_tag.delete()

    def __str__(self):
        return f"TicketTag: {self.created} for Team: {self.team.name}"

    def _pre_create(self):
        tag = self.tag
        ticket = self.ticket

        if not tag:
            raise ValueError("missing tag")

        if not ticket:
            raise ValueError("missing ticket")

        team_id = "{}".format(tag.id)
        ticket_id = "{}".format(ticket.id)
        self.id = (
            md5(team_id.encode()).hexdigest() + md5(ticket_id.encode()).hexdigest()
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()
        super(TicketTag, self).save(*args, **kwargs)
