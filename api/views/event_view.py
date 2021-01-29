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

class EventViewSet(TeamRelatedViewSet, mixins.DeleteModelMixin):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['^team__name', '^title', '^description', '^description', '^event_type',
                     '^user']
    ordering_fields = ['created', 'team', 'event_type', 'user']

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=[permissions.IsAuthenticated, IsMemberUser, IsAdminMemberOrReadOnly]
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            self.perform_destroy(instance)
            return Response({"msg": "okay"}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"msg": "no such event"}, status=status.HTTP_404_NOT_FOUND)

