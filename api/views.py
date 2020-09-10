from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import exceptions

from django.contrib.auth import get_user_model, get_user

from .models import (
    Member,
    Team,
    Ticket,
    TicketComment,
    TicketStatus
)
from .serializers import (
    TicketSerializer,
    MemberSerializer,
    TeamSerializer,
    TicketCommentSerializer,
    UserSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class MemberViewSet(viewsets.ModelViewSet):
    """
    CRUD stuff inherited from ModelViewSet
    """

    queryset = Member.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    serializer_class = MemberSerializer

    # i think it should be reasonable that when members are created, the authenticated user
    # is the one that the member record references
    def create(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")

        try:
            team = Team.objects.get(id=team_id)
            serializer = MemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save(user=self.request.user, team=team)

            headers = self.get_success_headers(serializer.data)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # this facilitates editing the user profile associated with a team
    # this function is keyed in by the join_id which is the team_id
    # concatenated with the md5 of the user_id
    #
    # affects both the member record and the associated user record
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        pk = kwargs.pop("pk")

        # serialize the input, then update only a select number of fields
        try:
            member_serializer = MemberSerializer(data=request.data)
            member_serializer.is_valid(raise_exception=True)
            member_data = member_serializer.validated_data

            user_serializer = UserSerializer(data=request.data.get("user"))
            user_serializer.is_valid(raise_exception=True)
            user_data = user_serializer.validated_data

            # only update the fields that the user has access to
            # in their edit profile dialog
            member = Member.objects.get(pk=pk)
            Member.objects.filter(pk=pk).update(
                bio=member_data.get("bio"),
            )

            get_user_model().objects.filter(pk=member.user.id).update(
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name")
            )

        except Member.DoesNotExist as e:
            return Response({"msg": e.message}, status=status.HTTP_404_NOT_FOUND)

        except exceptions.ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, partial=True)

    @action(detail=True, methods=["put"])
    def approve(self, request, pk=None):
        """ approve the join request """
        try:
            member = Member.objects.get(pk=pk)
            member.activated = timezone.now()
            member.save(update_fields=["activated"])

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["put"])
    def leave(self, request, pk=None):
        """ leave this team this is deletion but only to deactivate the record """

        try:
            member = Member.objects.get(pk=pk)
            member.deactivated = timezone.now()
            member.save()

            return Response({"msg": "okay"}, status=status.HTTP_200_OK)

        except Member.DoesNotExist:
            return Response({"msg": "failure"}, status=status.HTTP_404_NOT_FOUND)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        # IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

    serializer_class = TeamSerializer

    # requiring that all updates are partial instead of full
    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def search(self, request, search_term=None):
        """ retrieve teams based on a user search term. ideally i would want to use something like
            cosine similarity
        """
        pass


class TicketViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        # IsOwnerOrReadOnly | IsAdminOrReadOnly, ignoring these until we get owner field squared away
    ]

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(detail=False, methods=["get"])
    def list_team(self, request, pk=None):
        queryset = Ticket.objects.filter(team__id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """
    Basic crud should be pre-generated, so we only need to do the more complicated calls
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly,
    ]

    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer

    @action(detail=False)
    def recent_comments(self, request, team_id=None):
        """ This call returns the first page of comments associated with the given team_id """
        pass


class TicketStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly
    ]

    queryset = TicketStatus.objects.all()
