from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from api.serializers import TicketSerializer
from api.models import Ticket


class UserAssignedTickets(GenericViewSet, ListAPIView):
    queryset = Ticket.objects.all().prefetch_related("assigned_user")
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(assigned_user=user)
