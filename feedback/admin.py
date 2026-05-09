from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("incident", "citizen", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("incident__title", "citizen__email", "comment")
    autocomplete_fields = ("incident", "citizen")
