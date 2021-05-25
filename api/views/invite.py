from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from ..permissions import IsAuthenticated
from ..serializers import TeamSerializer, TeamInviteSerializer


class TeamInviteViewSet(GenericViewSet,
                        ListModelMixin,
                        CreateModelMixin,
                        DestroyModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = TeamInviteSerializer

    def list(self, request, *args, **kwargs):
        return Response({"msg": "hello world!"})

    def create(self, request, *args, **kwargs):
        return Response({"msg": "hello world!"})

    def destroy(self, request, *args, **kwargs):
        return Response({"msg": "hello world!"})


class UserInviteViewSet(GenericViewSet,
                        ListModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        pass

    @action()
    def accept_invite(self):
        pass
