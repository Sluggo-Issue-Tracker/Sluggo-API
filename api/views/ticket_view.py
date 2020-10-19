from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions

from django.contrib.auth import get_user_model, get_user

from ..models import Ticket, TicketComment, TicketStatus
from ..serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    TicketStatusSerializer,
)
from ..permissions import IsOwnerOrReadOnly, IsAdminMemberOrReadOnly


class TicketViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(detail=False, methods=["get"])
    def list_team(self, request, pk=None):
        queryset = Ticket.objects.filter(team__id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """
    Basic crud should be pre-generated, so we only need to do the more complicated calls
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly | IsAdminMemberOrReadOnly,
    ]

    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer

    @action(detail=False)
    def recent_comments(self, request, team_id=None):
        """ This call returns the first page of comments associated with the given team_id """
        pass


class TicketStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    queryset = TicketStatus.objects.all()
    serializer_class = TicketStatusSerializer
