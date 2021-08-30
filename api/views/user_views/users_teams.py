from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from api.serializers import TeamSerializer
from api.models import Team


class UsersTeamsViewSet(GenericViewSet, ListModelMixin):
    permissions_classes = [IsAuthenticated]
    serializer_class = TeamSerializer
    queryset = Team.objects.all().prefetch_related("member")
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(member__owner=user)
