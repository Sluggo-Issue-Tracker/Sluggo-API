from django.db import models

from .ticket import Ticket
from treebeard import mp_tree


# this file experiments with the treebeard library
class TicketNode(mp_tree.MP_Node):
    ticket = models.OneToOneField(
        Ticket, on_delete=models.CASCADE, related_name="ticket_node"
    )

    def __unicode__(self):
        return "Ticket :%s " % self.ticket.title
