from django.db import models
from .member import Member
from .ticket import Ticket
from .team import Team
from api.models.interfaces import HasUuid
from hashlib import md5


class PinnedTicket(HasUuid):
    id = models.CharField(max_length=256,
                          unique=True,
                          primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, editable=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, editable=True)
    pinned = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             editable=True,
                             null=False,
                             related_name="pinned_ticket")

    class Meta:
        ordering = ["pinned"]
        app_label = "api"
        unique_together = [["ticket", "member"]]

    def _pre_create(self):
        member = self.member
        ticket = self.ticket

        if not member:
            raise ValueError("Member not provided for pinned ticket relationship")

        if not ticket:
            raise ValueError("Ticket not provided for pinned ticket relationship")

        # Create ID
        member_id = "{}".format(member.id)
        ticket_id = "{}".format(ticket.id)

        self.id = md5(member_id.encode()).hexdigest() + md5(ticket_id.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self._pre_create()

        super(PinnedTicket, self).save(*args, **kwargs)

    def __str__(self):
        return("Ticket pin " + str(self.ticket.id) + " on team " +
               self.ticket.team.name + " for member " + self.member.owner.username)


