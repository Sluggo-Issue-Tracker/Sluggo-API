from django.db.models import Q
from rest_framework.decorators import action
from .team_related_base import *
from ..serializers import *
from ..permissions import *
from ..docs import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().prefetch_related('member')
    serializer_class = TeamSerializer
    permission_classes = [IsAdminMemberOrReadOnly, IsMemberUser, IsAuthenticated]

    search_fields = ['^name']
    ordering_fields = ['created', 'activated']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(member__owner=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # create a member record for the requesting user
        Member.objects.create(team=instance, owner=request.user, role=Member.Roles.ADMIN).save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
                     '^assigned_user__first_name']

    ordering_fields = ['created', 'activated']
    filterset_fields = ['assigned_user__owner__username']

    @extend_schema(**TEAM_DETAIL_SCHEMA)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(team=self.get_team())

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PinnedTicketViewSet(TeamRelatedListMixin,
                          TeamRelatedRetrieveMixin,
                          TeamRelatedDestroyMixin,
                          TeamRelatedCreateMixin):
    serializer_class = PinnedTicketSerializer
    permission_classes = [
        IsMemberUser, IsOwnerOrReadOnly, IsAuthenticated
    ]
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
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
        user_member = self.get_queryset(*args, **kwargs).get(owner=request.user)
        if not user_member.is_admin():
            request.data.pop('role', None)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class StatusViewSet(
    TeamRelatedModelViewSet
):
    queryset = TicketStatus.objects.all().select_related(
        'team'
    )
    serializer_class = TicketStatusSerializer


class TagViewSet(
    TeamRelatedModelViewSet
):
    queryset = Tag.objects.all().select_related(
        'team'
    )
    serializer_class = TagSerializer


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
