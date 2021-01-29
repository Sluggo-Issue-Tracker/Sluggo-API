from rest_framework.schemas import get_schema_view
from django.urls import include, path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views as api_views

router = DefaultRouter()

# social stuff
router.register(r"member", api_views.MemberViewSet)
router.register(r"team", api_views.TeamViewSet)

# ticket stuff
router.register(r"ticket", api_views.TicketViewSet)
router.register(r"ticket-comment", api_views.TicketCommentViewSet)
router.register(r"status", api_views.TicketStatusViewSet)
router.register(r"tag", api_views.TagViewSet)
router.register(r"event", api_views.EventViewSet)

urlpatterns = [
    # Optional UI:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("", include(router.urls)),

    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/slack/', api_views.SlackLogin.as_view(), name="slack_login"),

    path("api-auth/", include("rest_framework.urls")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls)
]
