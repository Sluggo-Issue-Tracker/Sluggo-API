from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView

from ..models import TeamInvite, Team
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



class UserInviteView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all().prefetch_related('member')

    def check_permissions(self, request):
        super().check_permissions(request)

    @api_view(['GET'])
    def list_teams(self, request, format=None) -> Response:

        teams = TeamSerializer(many=True, data=self.queryset.filter(member__owner=self.request.user))
        return Response(teams.data)