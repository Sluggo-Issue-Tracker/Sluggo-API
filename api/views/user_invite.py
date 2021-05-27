from rest_framework.views import APIView
from django.db import transaction

from ..serializers import TeamSerializer
from .team_related_base import *


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
