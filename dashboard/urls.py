from django.urls import path

from .views import DashboardView, ReportsView, StatisticsView


app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("reports/", ReportsView.as_view(), name="reports"),
]
