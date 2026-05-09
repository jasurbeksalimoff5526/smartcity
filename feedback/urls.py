from django.urls import path

from .views import FeedbackListView, feedback_create


app_name = "feedback"

urlpatterns = [
    path("", FeedbackListView.as_view(), name="feedback_list"),
    path("incident/<int:incident_pk>/", feedback_create, name="feedback_create"),
]
