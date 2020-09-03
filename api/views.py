from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .models import (
    Member,
    Team,
    Ticket,
    TicketComment,
    TicketStatus
)
from .serializers import (
    UserSerializer,
    TicketSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class TicketViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly,
    ]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MemberViewSet(viewsets.ModelViewSet):
    """
    list and detail inherited from parent class
    """

    queryset = Member.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

