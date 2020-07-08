"""
This project will house Andrew's testing of REST API things
"""
from django.urls import include, path
from . import views as snippet_views

urlpatterns = [
    path("snippets/", snippet_views.snippet_list),
    path("snippets/<int:pk>/", snippet_views.snippet_detail),
]
