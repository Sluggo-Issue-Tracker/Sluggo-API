import django_filters.rest_framework
from django.utils import timezone
from treebeard import exceptions as t_except
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import get_user_model

from ..models import (
    Event
)

from ..serializers import (
    EventSerializer
)

from .team_base import *
from ..permissions import IsUserOwnerOrReadOnly

class EventViewSet(TeamRelatedViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsUserOwnerOrReadOnly | IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['^team__name', '^title', '^description', '^description', '^event_type',
                     '^user']
    ordering_fields = ['created', 'team', 'event_type', 'user']
    