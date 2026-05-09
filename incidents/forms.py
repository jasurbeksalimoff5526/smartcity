from django import forms

from users.models import User

from .models import Category, Incident


def apply_bootstrap(form):
    for field in form.fields.values():
        field.widget.attrs.update({"class": "form-control"})
    return form


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)


class IncidentCreateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = (
            "category",
            "title",
            "description",
            "image",
            "latitude",
            "longitude",
            "address",
            "priority",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)


class IncidentAssignmentForm(forms.ModelForm):
    technician = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Technician",
    )

    class Meta:
        model = Incident
        fields = ("technician", "status", "priority")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].queryset = User.objects.filter(role=User.Role.TECHNICIAN)
        apply_bootstrap(self)


class IncidentResolutionForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ("resolution_note", "status")
        widgets = {
            "resolution_note": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = (
            (Incident.Status.IN_PROGRESS, "In progress"),
            (Incident.Status.RESOLVED, "Resolved"),
        )
        apply_bootstrap(self)

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        note = cleaned_data.get("resolution_note")
        if status == Incident.Status.RESOLVED and not note:
            self.add_error("resolution_note", "Resolution note is required.")
        return cleaned_data
