from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class TagViewSet(
    TeamRelatedModelViewSet
):
    queryset = Tag.objects.all().select_related(
        'team'
    )
    serializer_class = TagSerializer

    def create(self, request, *args, **kwargs):

        tag_serializer = self.get_serializer(data=request.data)
        tag_serializer.is_valid(raise_exception=True)

        title = tag_serializer.data.get("title")
        team_instance = self.get_team()

        if Tag.objects.filter(team=team_instance, title=title):
            raise serializers.ValidationError({"team": "a tag with this title already belongs to this team"})

        return super().create(request, args, kwargs)