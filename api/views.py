from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .models import Profile, Ticket
from .serializers import (
    ProfileSerializer,
    AdminProfileSerializer,
    UserSerializer,
    TicketSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class ProfileViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly,
    ]
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated and (
            self.action == "create"
            or self.request.user.profiles.role == Profile.Roles.ADMIN
        ):
            return AdminProfileSerializer
        else:
            return ProfileSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly | IsAdminOrReadOnly,
    ]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """


    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
