from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.views.generic import TemplateView

from feedback.models import Feedback
from incidents.models import Category, Incident
from users.decorators import RoleRequiredMixin
from users.models import User


class DashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = (User.Role.OPERATOR, User.Role.ADMIN)
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incidents = Incident.objects.all()
        context.update(
            {
                "total_incidents": incidents.count(),
                "resolved_incidents": incidents.filter(
                    status__in=[Incident.Status.RESOLVED, Incident.Status.CLOSED]
                ).count(),
                "pending_incidents": incidents.exclude(status=Incident.Status.CLOSED).count(),
                "high_priority_incidents": incidents.filter(
                    priority=Incident.Priority.HIGH
                ).count(),
                "average_rating": Feedback.objects.aggregate(avg=Avg("rating"))["avg"],
                "status_rows": incidents.values("status").annotate(total=Count("id")),
                "priority_rows": incidents.values("priority").annotate(total=Count("id")),
            }
        )
        return context


class StatisticsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = (User.Role.OPERATOR, User.Role.ADMIN)
    template_name = "dashboard/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(total=Count("incidents")).order_by(
            "-total", "name"
        )
        context["technicians"] = User.objects.filter(role=User.Role.TECHNICIAN).annotate(
            assigned_count=Count("assigned_incidents"),
            resolved_count=Count(
                "assigned_incidents",
                filter=Q(assigned_incidents__status__in=[
                    Incident.Status.RESOLVED,
                    Incident.Status.CLOSED,
                ]),
            ),
        )
        return context


class ReportsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = (User.Role.OPERATOR, User.Role.ADMIN)
    template_name = "dashboard/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["problem_locations"] = (
            Incident.objects.exclude(address="")
            .values("address")
            .annotate(total=Count("id"))
            .order_by("-total", "address")[:10]
        )
        context["problem_categories"] = Category.objects.annotate(
            total=Count("incidents")
        ).order_by("-total", "name")[:10]
        return context
