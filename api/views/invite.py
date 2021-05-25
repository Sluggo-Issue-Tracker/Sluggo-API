from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import TeamInvite
from ..permissions import IsAuthenticated, IsAdminMember
from ..serializers import TeamSerializer, TeamInviteSerializer
from .team_related_base import TeamRelatedListMixin, TeamRelatedCreateMixin, TeamRelatedDestroyMixin


class TeamInviteViewSet(TeamRelatedListMixin,
                        TeamRelatedCreateMixin,
                        TeamRelatedDestroyMixin):

    """
    This class is simple enough that the defautls for listing, creating, and destroying are sufficient
    """

    queryset = TeamInvite.objects.all().select_related('team')
    permission_classes = [IsAuthenticated, IsAdminMember]
    serializer_class = TeamInviteSerializer


class UserInviteViewSet(GenericViewSet,
                        ListModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        pass

    @action(detail=True)
    def accept_invite(self):
        pass
