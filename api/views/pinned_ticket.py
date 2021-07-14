from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class PinnedTicketViewSet(
    TeamRelatedListMixin,
    TeamRelatedRetrieveMixin,
    TeamRelatedDestroyMixin,
    TeamRelatedCreateMixin,
):
    serializer_class = PinnedTicketSerializer
    permission_classes = [IsMemberUser, IsOwnerOrReadOnly, IsAuthenticated]
    queryset = PinnedTicket.objects.all()
    pagination_class = None

    def get_member(self):
        member_id = self.kwargs.get(MEMBER_PK)
        return get_object_or_404(Member, pk=member_id)

    def get_queryset(self, *args, **kwargs):
        member_instance = self.get_member()
        team_instance = self.get_team()
        return self.queryset.filter(team=team_instance, member=member_instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save the instance
        team_instance = self.get_team()
        member_instance = self.get_member()

        serializer.save(team=team_instance, member=member_instance)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
