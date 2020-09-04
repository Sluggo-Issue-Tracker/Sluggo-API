from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import (
    Member,
    Team,
    Ticket,
    TicketComment,
    TicketStatus
)
from .serializers import (
    TicketSerializer,
    MemberSerializer,
    TeamSerializer,
    TicketCommentSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class MemberViewSet(viewsets.ModelViewSet):
    """
    CRUD stuff inherited from ModelViewSet
    """

    queryset = Member.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

    serializer_class = TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):

    queryset = Team.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

    serializer_class = MemberSerializer

    @action(detail=True, methods=["post"])
    def join(self, request):
        """ create a new member entry representing a join to the referenced """
        pass

    @action(detail=False, methods=["get"])
    def search(self, request, search_term=None):
        """ retrieve teams based on a user search term. ideally i would want to use something like
            cosine similarity
        """
        pass


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
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly,
    ]

    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer

    @action(detail=False)
    def recent_comments(self, request, team_id=None):
        """ This call returns the first page of comments associated with the given team_id """
        pass


class TicketStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

    queryset = TicketStatus.objects.all()
