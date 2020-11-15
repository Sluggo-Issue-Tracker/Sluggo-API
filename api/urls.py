"""
This project will house Andrew's testing of REST API things
"""
from django.urls import include, path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views as api_views

router = DefaultRouter()

# social stuff
router.register(r"member", api_views.MemberViewSet)
router.register(r"team", api_views.TeamViewSet)

team_search = api_views.TeamViewSet.as_view({
    'get': 'search'
})

# ticket stuff
router.register(r"ticket", api_views.TicketViewSet)
router.register(r"ticket-comment", api_views.TicketCommentViewSet)
router.register(r"status", api_views.TicketStatusViewSet)
router.register(r"ticket-tag", api_views.TicketTagViewSet)
router.register(r"tag", api_views.TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('team/search/<str:q>', team_search, name='team-search'),

    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration', include('dj_rest_auth.registration.urls')),

    path("api-auth/", include("rest_framework.urls")),
    path('admin/', admin.site.urls)
]
