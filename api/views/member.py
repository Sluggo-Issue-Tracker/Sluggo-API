from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class MemberViewSet(TeamRelatedModelViewSet):
    queryset = Member.objects.all().select_related(
        'team', 'owner'
    )
    serializer_class = MemberSerializer
    permission_classes = [
        IsMemberUserOrCreate, IsOwnerOrReadOnly | IsAdminMemberOrReadOnly, IsAuthenticated
    ]

    @extend_schema(**TEAM_DETAIL_SCHEMA)
    def create(self, request, *args, **kwargs):
        request.data.pop('role', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save the instance
        team_instance = self.get_team()
        serializer.save(owner=request.user, team=team_instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(**TEAM_DETAIL_SCHEMA)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # prevent the user updating roles if not admin
        user_member = self.get_queryset(
            *args, **kwargs).get(owner=request.user)
        if not user_member.is_admin():
            request.data.pop('role', None)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
