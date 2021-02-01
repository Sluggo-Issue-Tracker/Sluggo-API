from rest_framework.schemas import get_schema_view
from django.urls import include, path
from django.contrib import admin
from rest_framework.routers import DefaultRouter, SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_nested import routers

from . import views as api_views
from . import better_views

new_router = SimpleRouter()
new_router.register('new-team', better_views.TeamViewSet)

team_router = routers.NestedSimpleRouter(
    new_router,
    r'new-team',
    lookup='new_team'
)

team_router.register(
    r'tickets',
    better_views.TeamViewSet,
    basename='team-tickets'
)

#####################################################
# Below are the old urls that are getting refactored
#####################################################

old_router = DefaultRouter()

# social stuff
old_router.register(r"member", api_views.MemberViewSet)
old_router.register(r"team", api_views.TeamViewSet)

# ticket stuff
old_router.register(r"ticket", api_views.TicketViewSet)
old_router.register(r"ticket-comment", api_views.TicketCommentViewSet)
old_router.register(r"status", api_views.TicketStatusViewSet)
old_router.register(r"tag", api_views.TagViewSet)
old_router.register(r"event", api_views.EventViewSet)

urlpatterns = [
    # Optional UI:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("new/", include(new_router.urls)),
    path("new/", include(team_router.urls)),
    # path("", include(old_router.urls)),

    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/slack/', api_views.SlackLogin.as_view(), name="slack_login"),

    path("api-auth/", include("rest_framework.urls")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls)
]
print(
    'hello'
)