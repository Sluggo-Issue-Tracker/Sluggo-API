from rest_framework import status, viewsets, mixins
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from .models import Team, Ticket
from .serializers import TeamSerializer, TicketSerializer
from .permissions import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAdminMemberOrReadOnly, IsAuthenticated]


class NewTeamRelatedBase(viewsets.ModelViewSet):

    def get_queryset(self, *args, **kwargs):
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team, pk=team_id)
        return self.queryset.filter(team=team)


class TicketViewSet(NewTeamRelatedBase):
    """ Ticket Viewset """
    queryset = Ticket.objects.all().select_related(
        'team'
    ).prefetch_related(
        'owner', 'assigned_user', 'status'
    )
    serializer_class = TicketSerializer
    permission_classes = [
        IsMemberUser, IsOwnerOrReadOnly
    ]

