from django.contrib import admin

from .models import Category, Incident


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "priority",
        "citizen",
        "technician",
        "created_at",
    )
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = ("title", "description", "address", "citizen__email", "technician__email")
    autocomplete_fields = ("citizen", "technician", "category")
    readonly_fields = ("created_at", "updated_at")
