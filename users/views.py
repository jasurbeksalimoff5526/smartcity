from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginForm, RegisterForm


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "auth/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("incidents:incident_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi.")
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"
