from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class EventViewSet(TeamRelatedListMixin,
                   TeamRelatedUpdateMixin,
                   TeamRelatedRetrieveMixin,
                   TeamRelatedDestroyMixin):
    permission_classes = [
        IsAuthenticated,
        IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]
    queryset = Event.objects.all().select_related(
        'team'
    ).prefetch_related(
        'user'
    )
    serializer_class = EventSerializer
