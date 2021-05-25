from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import TeamInvite, Team, Member
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

    def create(self, request, *args, **kwargs):

        invite_serializer = self.get_serializer(request.data)
        invite_serializer.is_valid(raise_exception=True)
        invite_instance: TeamInvite = invite_serializer.instance

        member_queryset = Member.objects.filter(team=invite_instance.team, owner=invite_instance.user)
        if member_queryset:
            return Response({"msg", "cannot create an invite for a member that already exists!"})

        return super().create(request, *args, **kwargs)


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
            member_instance = Member.objects.create(team=team_instance, owner=request.user)
            member_instance.save()
            invite_instance.delete()

        return Response({"msg": "success"})
