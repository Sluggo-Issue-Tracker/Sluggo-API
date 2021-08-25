from rest_framework.routers import SimpleRouter
from api.views.user_views.pinned_tickets import UserPinnedTickets
from api.views.user_views.user_invite import UserInviteViewSet
from api.views.user_views.assigned_tickets import UserAssignedTickets


def buildUserRouterUrls() -> list:
    router = SimpleRouter()
    router.register("pinned-tickets", UserPinnedTickets)
    router.register("assigned-tickets", UserAssignedTickets)
    router.register("invites", UserInviteViewSet)
    return router.urls
