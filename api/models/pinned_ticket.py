from django.db import models
from .member import Member
from .ticket import Ticket
from api.models.interfaces import HasUuid, TeamRelated
from hashlib import md5


class PinnedTicket(HasUuid, TeamRelated):
    id = models.CharField(max_length=256,
                          unique=True,
                          editable=False,
                          primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    pinned = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["pinned"]
        app_label = "api"

    def save(self, *args, **kwargs):
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

        super(PinnedTicket, self).save(*args, **kwargs)


