from rest_framework import permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.settings import api_settings

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
    mixins.ListModelMixin,
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

    @staticmethod
    def get_success_headers(data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(detail=False, methods=["get"])
    def list_team(self, request, pk=None):
        queryset = Ticket.objects.filter(team__id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    # require that the user is a member of the team to create a ticket
    # manually defining this since we want to offer this endpoint for any authenticated user
    @action(
        methods=["POST"], detail=False,
    )
    def create_record(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")
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
            return Response({"msg": e.message}, status=status.HTTP_404_NOT_FOUND)
        except Member.DoesNotExist as e:
            return Response({"msg": e.message}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[
            permissions.IsAuthenticated,
            IsOwnerOrReadOnly | IsAdminMemberOrReadOnly,
        ],
    )
    def delete(self, request, pk=None):
        """ deactivate this ticket this is deletion but only to deactivate the record """
        try:
            ticket = Ticket.objects.get(pk=pk)
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


class TicketStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    queryset = TicketStatus.objects.all()
    serializer_class = TicketStatusSerializer
