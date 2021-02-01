from rest_framework import status, viewsets, mixins
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import *
from .models.interfaces import team_related
from .serializers import TeamSerializer, TicketSerializer, MemberSerializer
from .permissions import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAdminMemberOrReadOnly, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # create a member record for the requesting user
        Member.objects.create(team=instance, owner=request.user, role=Member.Roles.ADMIN).save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class NewTeamRelatedBase(viewsets.ModelViewSet):

    def get_team(self, *args, **kwargs):
        team_id = self.kwargs.get("new_team_pk")
        return get_object_or_404(Team, pk=team_id)

    def get_queryset(self, *args, **kwargs):
        team_instance = self.get_team(*args, **kwargs)
        return self.queryset.filter(team=team_instance)


class TicketViewSet(NewTeamRelatedBase):
    """ Ticket Viewset """
    queryset = Ticket.objects.all().select_related(
        'team'
    ).prefetch_related(
        'owner', 'assigned_user', 'status'
    )
    serializer_class = TicketSerializer
    permission_classes = [
        IsMemberUser, IsOwnerOrReadOnly
    ]


class MemberViewSet(NewTeamRelatedBase):
    queryset = Member.objects.all().select_related(
        'team'
    ).prefetch_related(
        'owner'
    )
    serializer_class = MemberSerializer
    permission_classes = [
        IsMemberUser, IsOwnerOrReadOnly
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save the instance
        team_instance = self.get_team(*args, **kwargs)
        serializer.save(owner=request.user, team=team_instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
