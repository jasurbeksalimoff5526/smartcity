from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from users.decorators import RoleRequiredMixin, has_role
from users.models import User

from .forms import (
    CategoryForm,
    IncidentAssignmentForm,
    IncidentCreateForm,
    IncidentResolutionForm,
)
from .models import Category, Incident


def can_view_incident(user, incident):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.OPERATOR:
        return user.categories.filter(pk=incident.category_id).exists()
    if user.role == User.Role.CITIZEN:
        return incident.citizen_id == user.id
    if user.role == User.Role.TECHNICIAN:
        return incident.technician_id == user.id
    return False


class IncidentListView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = "incidents/incident_list.html"
    context_object_name = "incidents"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Incident.objects.select_related("citizen", "technician", "category")
            .all()
        )
        user = self.request.user

        if user.role == User.Role.CITIZEN:
            queryset = queryset.filter(citizen=user)
        elif user.role == User.Role.TECHNICIAN:
            queryset = queryset.filter(technician=user)
        elif user.role == User.Role.OPERATOR and not user.is_superuser:
            queryset = queryset.filter(category__in=user.categories.all())

        status = self.request.GET.get("status")
        category = self.request.GET.get("category")
        priority = self.request.GET.get("priority")
        query = self.request.GET.get("q")

        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category_id=category)
        if priority:
            queryset = queryset.filter(priority=priority)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(address__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["status_choices"] = Incident.Status.choices
        context["priority_choices"] = Incident.Priority.choices
        context["filters"] = self.request.GET
        return context


class IncidentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Incident
    template_name = "incidents/incident_detail.html"
    context_object_name = "incident"
    queryset = Incident.objects.select_related("citizen", "technician", "category")

    def test_func(self):
        return can_view_incident(self.request.user, self.get_object())


class IncidentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = (User.Role.CITIZEN,)
    model = Incident
    form_class = IncidentCreateForm
    template_name = "incidents/incident_create.html"

    def form_valid(self, form):
        form.instance.citizen = self.request.user
        form.instance.status = Incident.Status.NEW
        messages.success(self.request, "Incident yaratildi va operatorlarga yuborildi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("incidents:incident_detail", kwargs={"pk": self.object.pk})


class IncidentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Incident
    form_class = IncidentCreateForm
    template_name = "incidents/incident_update.html"

    def get_queryset(self):
        return Incident.objects.filter(citizen=self.request.user, status=Incident.Status.NEW)

    def test_func(self):
        return self.request.user.role == User.Role.CITIZEN

    def form_valid(self, form):
        messages.success(self.request, "Incident ma'lumotlari yangilandi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("incidents:incident_detail", kwargs={"pk": self.object.pk})


class IncidentAssignView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    allowed_roles = (User.Role.OPERATOR, User.Role.ADMIN)
    model = Incident
    form_class = IncidentAssignmentForm
    template_name = "incidents/incident_assign.html"

    def get_queryset(self):
        queryset = Incident.objects.select_related("category")
        user = self.request.user

        if user.is_superuser or user.role == User.Role.ADMIN:
            return queryset

        return queryset.filter(category__in=user.categories.all())

    def form_valid(self, form):
        incident = form.save(commit=False)
        if incident.technician and incident.status == Incident.Status.NEW:
            incident.status = Incident.Status.IN_PROGRESS
        incident.save()
        messages.success(self.request, "Incident technician ga biriktirildi.")
        return redirect("incidents:incident_detail", pk=incident.pk)


class IncidentResolveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Incident
    form_class = IncidentResolutionForm
    template_name = "incidents/incident_resolve.html"

    def get_queryset(self):
        queryset = Incident.objects.select_related("technician")
        if self.request.user.role == User.Role.TECHNICIAN:
            queryset = queryset.filter(technician=self.request.user)
        return queryset

    def test_func(self):
        incident = self.get_object()
        return (
            has_role(self.request.user, User.Role.ADMIN, User.Role.OPERATOR)
            or incident.technician_id == self.request.user.id
        )

    def form_valid(self, form):
        messages.success(self.request, "Incident yechimi saqlandi.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("incidents:incident_detail", kwargs={"pk": self.object.pk})


@require_POST
def close_incident(request, pk):
    if not request.user.is_authenticated:
        raise PermissionDenied

    incident = get_object_or_404(Incident, pk=pk, citizen=request.user)
    if incident.status != Incident.Status.RESOLVED:
        raise PermissionDenied

    incident.status = Incident.Status.CLOSED
    incident.save(update_fields=["status", "updated_at"])
    messages.success(request, "Incident yopildi.")
    return redirect("incidents:incident_detail", pk=incident.pk)


class CategoryListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.ADMIN,)
    model = Category
    template_name = "incidents/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = (User.Role.ADMIN,)
    model = Category
    form_class = CategoryForm
    template_name = "incidents/category_form.html"
    success_url = reverse_lazy("incidents:category_list")


class CategoryUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    allowed_roles = (User.Role.ADMIN,)
    model = Category
    form_class = CategoryForm
    template_name = "incidents/category_form.html"
    success_url = reverse_lazy("incidents:category_list")
