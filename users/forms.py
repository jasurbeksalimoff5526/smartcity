from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("full_name", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "full_name": "Full name",
            "email": "Email",
            "phone": "Phone",
            "password1": "Password",
            "password2": "Confirm password",
        }
        for field_name, field in self.fields.items():
            field.label = labels.get(field_name, field.label)
            field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.role = User.Role.CITIZEN
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = "Email"
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
