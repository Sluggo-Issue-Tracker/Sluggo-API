from .team_related_base import *
from rest_framework import serializers
from api.serializers import *
from api.docs import *


class StatusViewSet(TeamRelatedModelViewSet):
    queryset = TicketStatus.objects.all().select_related("team")
    serializer_class = TicketStatusSerializer
    pagination_class = None


    @extend_schema(**TEAM_LIST_SCHEME)
    def create(self, request, *args, **kwargs):

        status_serializer = self.get_serializer(data=request.data)
        status_serializer.is_valid(raise_exception=True)

        title = status_serializer.data.get("title")
        team_instance = self.get_team()

        if TicketStatus.objects.filter(team=team_instance, title=title).exists():
            raise serializers.ValidationError(
                {"team": "a status of this title for this team already exists"}
            )

        return super().create(request, args, kwargs)
