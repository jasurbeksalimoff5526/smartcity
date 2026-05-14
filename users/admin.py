from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.exceptions import ValidationError

from .models import User


class UserAdminForm(forms.ModelForm):

    class Meta:
        model = User
        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        role = cleaned_data.get("role")
        categories = cleaned_data.get("categories")

        allowed_roles = {
            User.Role.OPERATOR,
            User.Role.TECHNICIAN,
        }

        if (
            role not in allowed_roles
            and categories
            and categories.exists()
        ):
            raise ValidationError(
                "Only operator and technician "
                "can have categories."
            )

        return cleaned_data


@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    form = UserAdminForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    ordering = (
        "username",
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
        "categories",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),

        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "role",
                    "categories",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "role",
                    "categories",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),

    )