from rest_framework.views import APIView
from django.db import transaction
from django.contrib.auth import get_user_model

from ..serializers import TeamSerializer, TeamInviteSerializer, serializers
from .team_related_base import *


class TeamInviteViewSet(TeamRelatedModelViewSet):

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


class UserInviteView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all().prefetch_related('invite')

    def get(self, request) -> Response:
        teams = TeamSerializer(self.queryset.filter(invite__user=self.request.user), many=True)
        return Response(teams.data)

    def post(self, request) -> Response:
        team_name = request.data.get('name', None)

        team_instance = get_object_or_404(Team, name=team_name)
        invite_instance = get_object_or_404(TeamInvite, team=team_instance, user=request.user)

        # this should guarantee that if failure occurs, the db won't get into a weird state
        with transaction.atomic():
            # silently fail for now.
            member_instance, _ = Member.objects.get_or_create(team=team_instance, owner=request.user)
            member_instance.save()
            invite_instance.delete()

        return Response({"msg": "success"})
