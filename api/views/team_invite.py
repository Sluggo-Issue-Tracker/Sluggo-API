from rest_framework.views import APIView
from django.db import transaction
from django.contrib.auth import get_user_model

from ..serializers import TeamSerializer, TeamInviteSerializer, serializers
from .team_related_base import *


class TeamInviteViewSet(TeamRelatedListMixin,
                        TeamRelatedCreateMixin,
                        TeamRelatedDestroyMixin):
    """
    This class is simple enough that the defautls for listing, creating, and destroying are sufficient
    """

    queryset = TeamInvite.objects.all().select_related('team')
    permission_classes = [IsAuthenticated, IsAdminMember]
    serializer_class = TeamInviteSerializer

    @extend_schema(**TEAM_LIST_SCHEME)
    def create(self, request, *args, **kwargs):

        invite_serializer = self.get_serializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)
        invited_user_json = invite_serializer.validated_data.get("user")

        invited_user = get_object_or_404(get_user_model(), email=invited_user_json.get("email"))
        team_instance = self.get_team()

        if Member.objects.filter(team=team_instance, owner=invited_user).exists():
            raise serializers.ValidationError({"member": "this already belongs to this team"})

        if TeamInvite.objects.filter(team=team_instance, user=invited_user).exists():
            raise serializers.ValidationError({"team": "an invite for this team and user already exists"})

        invite_serializer.save(team=team_instance, user=invited_user)

        return Response(invite_serializer.data, status=status.HTTP_201_CREATED)



