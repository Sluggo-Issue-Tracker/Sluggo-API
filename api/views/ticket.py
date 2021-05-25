from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class TicketViewSet(TeamRelatedModelViewSet):
    """ Ticket Viewset """
    queryset = Ticket.objects.all().select_related(
        'team', 'assigned_user', 'status'
    ).prefetch_related(
        'tag_list'
    )
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsMemberUser]

    search_fields = ['^team__name', '^team__description', '^title', '^description', '^status__title',
                     '^assigned_user__owner__username', '^tag_list__title']

    ordering_fields = ['created', 'activated']
    filterset_fields = ['assigned_user__owner__username',
                        'status__id', 'tag_list__id']

    @extend_schema(**TEAM_DETAIL_SCHEMA)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(team=self.get_team())

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
