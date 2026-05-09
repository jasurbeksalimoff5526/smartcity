from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from incidents.models import Incident
from users.decorators import RoleRequiredMixin
from users.models import User

from .forms import FeedbackForm
from .models import Feedback


class FeedbackListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.OPERATOR, User.Role.ADMIN)
    model = Feedback
    template_name = "feedback/feedback_list.html"
    context_object_name = "feedbacks"
    paginate_by = 15
    queryset = Feedback.objects.select_related("incident", "citizen")


def feedback_create(request, incident_pk):
    if not request.user.is_authenticated:
        raise PermissionDenied
    if request.user.role != User.Role.CITIZEN:
        raise PermissionDenied

    incident = get_object_or_404(Incident, pk=incident_pk, citizen=request.user)
    if incident.status not in {Incident.Status.RESOLVED, Incident.Status.CLOSED}:
        raise PermissionDenied

    feedback = Feedback.objects.filter(incident=incident, citizen=request.user).first()

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            saved_feedback = form.save(commit=False)
            saved_feedback.incident = incident
            saved_feedback.citizen = request.user
            saved_feedback.save()
            if incident.status == Incident.Status.RESOLVED:
                incident.status = Incident.Status.CLOSED
                incident.save(update_fields=["status", "updated_at"])
            messages.success(request, "Feedback saqlandi.")
            return redirect("incidents:incident_detail", pk=incident.pk)
    else:
        form = FeedbackForm(instance=feedback, initial={"rating": 5})

    return render(
        request,
        "feedback/feedback_form.html",
        {"form": form, "incident": incident},
    )
