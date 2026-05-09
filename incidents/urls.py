from django.urls import path

from .views import (
    CategoryCreateView,
    CategoryListView,
    CategoryUpdateView,
    IncidentAssignView,
    IncidentCreateView,
    IncidentDetailView,
    IncidentListView,
    IncidentResolveView,
    IncidentUpdateView,
    close_incident,
)


app_name = "incidents"

urlpatterns = [
    path("", IncidentListView.as_view(), name="incident_list"),
    path("create/", IncidentCreateView.as_view(), name="incident_create"),
    path("<int:pk>/", IncidentDetailView.as_view(), name="incident_detail"),
    path("<int:pk>/edit/", IncidentUpdateView.as_view(), name="incident_update"),
    path("<int:pk>/assign/", IncidentAssignView.as_view(), name="incident_assign"),
    path("<int:pk>/resolve/", IncidentResolveView.as_view(), name="incident_resolve"),
    path("<int:pk>/close/", close_incident, name="incident_close"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/create/", CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_update"),
]
