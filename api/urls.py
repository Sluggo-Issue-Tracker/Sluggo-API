"""
This project will house Andrew's testing of REST API things
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views as api_views

router = DefaultRouter()
router.register(r"users", api_views.UserViewSet, "api")
router.register(r"profiles", api_views.ProfileViewSet)
router.register(r"tickets", api_views.TicketViewSet)


urlpatterns = [path("", include(router.urls))]


urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]
