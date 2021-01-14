from django.utils import timezone
from treebeard import exceptions as t_except
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import get_user_model

from ..models import (
    Ticket,
    TicketComment,
    TicketStatus,
    Tag,
    TicketTag,
    TicketNode
)

from ..serializers import (
    TicketSerializer,
    TicketCommentSerializer,
    TicketStatusSerializer,
    TagSerializer,
    TicketNodeSerializer
)

from .team_base import *

User = get_user_model()


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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response = serializer.data
        root = TicketNode.objects.get(ticket=instance)
        if root:
            response["children"] = [TicketNodeSerializer(child_instance).data for child_instance in root.get_children()]

        return Response(response)

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

    def _add_subticket(self, parent, child):
        try:
            # fetch the associated node
            parent_node = get_object_or_404(TicketNode, ticket=parent)
            ticket_node_filter = TicketNode.objects.filter(ticket=child)

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
                parent_node.add_child(ticket=child)

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)
        except (
                t_except.InvalidMoveToDescendant, t_except.InvalidPosition,
                t_except.NodeAlreadySaved, t_except.PathOverflow
        ):
            return Response({"msg": "invalid tree operation"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=permission_classes
    )
    def add_as_subticket(self, request, pk=None):
        try:
            # validate
            ticket = self.get_object()
            parent = get_object_or_404(Ticket, pk=request.data.get("parent_id"))
            self.check_object_permissions(request, ticket)
            self.check_object_permissions(request, parent)

            # serialize the parent ticket

            return self._add_subticket(parent, ticket)

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
            child = get_object_or_404(Ticket, pk=request.data.get("child_id", None))
            self.check_object_permissions(request, parent)
            self.check_object_permissions(request, child)

            return self._add_subticket(parent, child)

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
