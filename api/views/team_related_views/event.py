from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from api.serializers import *
from api.permissions import *
from api.docs import *


class EventViewSet(
    TeamRelatedListMixin,
    TeamRelatedUpdateMixin,
    TeamRelatedRetrieveMixin,
    TeamRelatedDestroyMixin,
):
    permission_classes = [IsAuthenticated, IsAdminMemberOrReadOnly, IsMemberUser]
    queryset = Event.objects.all().select_related("team").prefetch_related("user")
    serializer_class = EventSerializer
