from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse

from .models import UserProfile


class RoleBasedLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # Staff users without a profile can access Django Admin.
        if not user.is_staff and not user.is_superuser:
            try:
                user.profile
            except UserProfile.DoesNotExist:
                messages.error(
                    self.request,
                    "Your account has no assigned role. Contact the administrator.",
                )
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return reverse("admin:index")

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return reverse("login")

        if profile.role == UserProfile.Role.MAKER:
            return reverse("maker_dashboard")

        if profile.role == UserProfile.Role.CHECKER:
            return reverse("checker_dashboard")

        return reverse("login")
