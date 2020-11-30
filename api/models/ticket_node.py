from django.db import models
from django.conf import settings

from .ticket import Ticket
from treebeard import mp_tree


# this file experiments with the treebeard library
class TicketNode(mp_tree.MP_Node):
    name = models.CharField(max_length=30)

    node_order_by = ['name']

    def __unicode__(self):
        return "Category :%s " % self.name
