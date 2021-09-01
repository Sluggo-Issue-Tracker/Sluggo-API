from rest_framework import serializers

from .team_related_base import *
from api.serializers import *


class TagViewSet(TeamRelatedModelViewSet):
    queryset = Tag.objects.all().select_related("team")
    serializer_class = TagSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):

        tag_serializer = self.get_serializer(data=request.data)
        tag_serializer.is_valid(raise_exception=True)

        title = tag_serializer.data.get("title")
        team_instance = self.get_team()

        if Tag.objects.filter(team=team_instance, title=title):
            raise serializers.ValidationError(
                {"team": "a tag with this title already belongs to this team"}
            )

        return super().create(request, args, kwargs)
