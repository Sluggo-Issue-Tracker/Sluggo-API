from rest_framework import permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.settings import api_settings
from rest_framework import filters
from rest_framework import serializers

from django.contrib.auth import get_user_model

from ..permissions import IsAdminMemberOrReadOnly, IsOwnerOrReadOnly, IsMemberUser

from ..models import (
    Ticket,
    TicketComment,
    TicketStatus,
    Member,
    Team,
)

from ..serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    TicketStatusSerializer,
)

User = get_user_model()

class TicketViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Ticket.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly | IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]
    serializer_class = TicketSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^team__name', '^team__description', '^title', '^description', '^status__title',
                     '^assigned_user__first_name'
                     ]
    ordering_fields = ['created', 'activated']

    @staticmethod
    def get_success_headers(data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(detail=True, methods=["GET"], permission_classes=permission_classes)
    def list_team(self, request, pk=None):

        queryset = self.filter_queryset(self.get_queryset().filter(team__id=pk))
        serializer = self.serializer_class(queryset, many=True)

        try:
            team = Team.objects.get(pk=pk)
            self.check_object_permissions(request, team)
            response = Response(serializer.data, status.HTTP_200_OK)
        except Team.DoesNotExist:
            response = Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

        return response

    # require that the user is a member of the team to create a ticket
    # manually defining this since we want to offer this endpoint for any authenticated user
    @action(
        methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def create_record(self, request, *args, **kwargs):
        '''team_id = request.data.get("team_id")
        assigned_id = request.data.get("assigned_id")
        try:
            team = Team.objects.get(id=team_id)
            assigned_user = User.objects.get(id=assigned_id)
            is_approved_user = Member.objects.get(owner=assigned_user)
            serializer = TicketSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(
                owner=self.request.user, team=team, assigned_user=assigned_user,
            )

            headers = self.get_success_headers(serializer.data)

        except Team.DoesNotExist as e:
            return Response({"msg": "team_id is a required field"}, status=status.HTTP_404_NOT_FOUND)

        except Member.DoesNotExist as e:
            return Response({"msg": "failure"}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )'''

        try:
            serializer = TicketSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            team = serializer.validated_data["team_id"]

            # once we have a team record, make sure we are allowed to access it
            self.check_object_permissions(request, team)
            ticket = serializer.save(
                owner=self.request.user
            )

            serialized = TicketSerializer(ticket)

            return Response(serialized.data, status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"msg": e.detail}, e.status_code)

    # note: this is pretty hacky
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = TicketSerializer(instance)
        return Response(serializer.data)


    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def update_status(self, request, pk=None):
        self.check_object_permissions(request, self.get_object())

        status_id = request.data('status_id')
        ticket = Ticket.objects.get(pk=pk)
        status = TicketStatus.objects.get(pk=status_id)
        ticket.status = status
        ticket.save(update_fields=['status'])

        return Response({"msg": "okay"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=permission_classes,
    )
    def delete(self, request, pk=None):
        """ deactivate this ticket this is deletion but only to deactivate the record """
        try:
            self.check_object_permissions(request, self.get_object())
            ticket = self.get_object()
            ticket.deactivated = timezone.now()
            ticket.save()
            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Ticket.DoesNotExist:
            return Response({"msg": "failure"}, status=status.HTTP_404_NOT_FOUND)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """
    Basic crud should be pre-generated, so we only need to do the more complicated calls
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly | IsAdminMemberOrReadOnly,
    ]

    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer

    @action(detail=False)
    def recent_comments(self, request, team_id=None):
        """ This call returns the first page of comments associated with the given team_id """
        pass


class TicketStatusViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsMemberUser,
        IsAdminMemberOrReadOnly
    ]

    queryset = TicketStatus.objects.all()
    serializer_class = TicketStatusSerializer

    @action(
        methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def create_record(self, request, *args, **kwargs):
        try:
            serializer = TicketStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            team = serializer.validated_data["team_id"]

            # make sure we're actually allowed to access this team
            self.check_object_permissions(request, team)
            status = serializer.save()

            serialized = TicketStatusSerializer(status)
            return Response(serialized.data, status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"msg": e.detail}, e.status_code)

    # this is a duplicate and should eventually get moved to a base class
    @action(detail=True, methods=["GET"], permission_classes=permission_classes)
    def list_team(self, request, pk=None):

        queryset = self.filter_queryset(self.get_queryset().filter(team__id=pk))
        serializer = self.serializer_class(queryset, many=True)

        try:
            team = Team.objects.get(pk=pk)
            self.check_object_permissions(request, team)
            response = Response(serializer.data, status.HTTP_200_OK)
        except Team.DoesNotExist:
            response = Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

        return response

    # note: this is pretty hacky
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)
