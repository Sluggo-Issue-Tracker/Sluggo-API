from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from api.serializers import TicketSerializer
from api.models import Ticket


class UserPinnedTickets(GenericViewSet, ListModelMixin):
    queryset = Ticket.objects.prefetch_related("members_pins")
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(members_pins__owner=user)
