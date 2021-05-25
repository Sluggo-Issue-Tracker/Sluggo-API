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
