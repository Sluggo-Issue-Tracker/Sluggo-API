from rest_framework import permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.settings import api_settings
from rest_framework import filters
from rest_framework import serializers
from treebeard import exceptions as t_except
from django.shortcuts import get_object_or_404
from django.core.exceptions import SuspiciousOperation

from django.contrib.auth import get_user_model

from ..permissions import IsAdminMemberOrReadOnly, IsOwnerOrReadOnly, IsMemberUser

from ..models import (
    Ticket,
    TicketComment,
    TicketStatus,
    Team,
    Tag,
    TicketTag,
    TicketNode
)

from ..serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    TicketStatusSerializer,
    TagSerializer,
    TicketTagSerializer
)

User = get_user_model()


class TeamRelatedViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]

    @staticmethod
    def get_success_headers(data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(
        methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def create_record(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            team = serializer.validated_data["team_id"]

            # make sure we're actually allowed to access this team
            self.check_object_permissions(request, team)
            record = serializer.save()

            serialized = self.serializer_class(record)
            return Response(serialized.data, status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"msg": e.detail}, e.status_code)

    @action(detail=True, methods=["GET"], permission_classes=permission_classes)
    def list_team(self, request, pk=None):

        queryset = self.filter_queryset(self.get_queryset().filter(team__id=pk))
        serializer = self.serializer_class(queryset, many=True)

        team = get_object_or_404(Team, pk=pk)
        self.check_object_permissions(request, team)
        return Response(serializer.data, status.HTTP_200_OK)

    # note: this is pretty hacky
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)


class TicketViewSet(
    TeamRelatedViewSet
):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^team__name', '^team__description', '^title', '^description', '^status__title',
                     '^assigned_user__first_name']
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly | IsAdminMemberOrReadOnly,
        IsMemberUser,
    ]
    ordering_fields = ['created', 'activated']

    def retrieve(self, request, *args, **kwargs):
        # the hackiness continues. i'm sorry little one
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            ticket_node = get_object_or_404(TicketNode, pk=self.get_object().pk)

            response.data["children"] = []
            for child_node in ticket_node.get_children():
                child = TicketSerializer(child_node.ticket)
                response.data["children"].append(child.data)

        return response

    # require that the user is a member of the team to create a ticket
    # manually defining this since we want to offer this endpoint for any authenticated user
    @action(
        methods=["POST"], detail=False, permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def create_record(self, request, *args, **kwargs):
        try:
            serializer = TicketSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            team = serializer.validated_data["team_id"]
            tag_list = serializer.validated_data.pop("tag_id_list", None)
            parent_id = serializer.validated_data.pop("parent_id", None)

            # once we have a team record, make sure we are allowed to access it
            self.check_object_permissions(request, team)
            ticket = serializer.save(
                owner=self.request.user
            )

            # the above serializer has already confirmed that each tag_id is valid
            if tag_list:
                for tag in tag_list:
                    ticket_tag = TicketTag.objects.create(
                        team=team, tag=tag, ticket=ticket
                    )
                    ticket_tag.save()

            # query for the parent. If the id was included, query for the
            # associated root node. if not, insert the ticket as a root
            if parent_id:
                parent_ticket = get_object_or_404(Ticket, pk=parent_id)
                parent_node = get_object_or_404(TicketNode, ticket=parent_ticket)
                parent_node.add_child(ticket=ticket)
            else:
                TicketNode.add_root(ticket=ticket)

            serialized = TicketSerializer(ticket)

            return Response(serialized.data, status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"msg": e.detail}, e.status_code)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAuthenticated, IsMemberUser]
    )
    def update_status(self, request, pk=None):
        self.check_object_permissions(request, self.get_object())

        status_id = request.data('status_id')
        ticket = get_object_or_404(Ticket, pk=pk)
        ticket_status = get_object_or_404(TicketStatus, pk=status_id)
        ticket.status = ticket_status
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
            instance = get_object_or_404(Ticket, pk=pk)
            self.check_object_permissions(request, instance)
            instance.deactivated = timezone.now()
            instance.save()
            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Ticket.DoesNotExist:
            return Response({"msg": "no such ticket"}, status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=permission_classes
    )
    def add_as_subticket(self, request, pk=None):
        try:
            # validate
            ticket = self.get_object()
            self.check_object_permissions(request, ticket)

            # serialize the parent ticket
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            parent_id = serializer.validated_data["parent_id"]
            parent = get_object_or_404(Ticket, pk=parent_id)

            # fetch the associated node
            parent_node = get_object_or_404(TicketNode, ticket=parent)
            ticket_node_filter = TicketNode.objects.filter(ticket=ticket)

            if ticket_node_filter:
                # if it exists and is root, move as child
                if len(ticket_node_filter) != 1:
                    raise SuspiciousOperation("Invalid request; the tree got messed up")

                ticket_node = ticket_node_filter[0]
                if ticket_node.is_root():
                    ticket_node.move(target=parent_node, pos="last-child")
                else:
                    return Response({"msg": "ticket already part of a graph"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                parent_node.add_child(ticket=ticket)

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except (
                t_except.InvalidMoveToDescendant, t_except.InvalidPosition,
                t_except.NodeAlreadySaved, t_except.PathOverflow
        ):
            return Response({"msg": "invalid tree operation"}, status=status.HTTP_400_BAD_REQUEST)

        except serializers.ValidationError as e:
            return Response({"msg": e.detail}, e.status_code)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=permission_classes
    )
    def add_subticket(self, request, pk=None):
        try:
            # validate
            parent = self.get_object()
            self.check_object_permissions(request, parent)

            # serialize the child ticket
            child_ticket = self.serializer_class(data=request.data)
            child_ticket.is_valid(raise_exception=True)
            child_id = child_ticket.validated_data["id"]
            child = get_object_or_404(Ticket, pk=child_id)

            # fetch the associated nodes
            parent_node = get_object_or_404(TicketNode, ticket=parent)
            ticket_node_filter = TicketNode.objects.filter(ticket=child)

            if ticket_node_filter:
                # if it exists and is root, move as child
                if len(ticket_node_filter) != 1:
                    raise SuspiciousOperation("Invalid request; the tree got messed up")

                child_node = ticket_node_filter[0]
                if child_node.is_root():
                    child_node.move(target=parent_node, pos="last-child")
                else:
                    return Response({"msg": "ticket already part of a graph"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                parent_node.add_child(ticket=child)

        except (
                t_except.InvalidMoveToDescendant, t_except.InvalidPosition,
                t_except.NodeAlreadySaved, t_except.PathOverflow
        ):
            return Response({"msg": "invalid tree operation"}, status=status.HTTP_400_BAD_REQUEST)

        except serializers.ValidationError as e:
            return Response({'msg': e.detail}, e.status_code)


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
    TeamRelatedViewSet,
    mixins.DestroyModelMixin
):
    queryset = TicketStatus.objects.all()
    serializer_class = TicketStatusSerializer


class TagViewSet(
    TeamRelatedViewSet,
    mixins.DestroyModelMixin
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
