from rest_framework import permissions, viewsets
from django.contrib.auth import get_user_model

from .models import Profile, Ticket
from .serializers import ProfileSerializer, UserSerializer, TicketSerializer
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
    serializer_class = ProfileSerializer


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
