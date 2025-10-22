from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    """Simple profile page that requires authentication."""
    template_name = 'users/profile.html'

    # Optionally customize the login redirect URL (defaults to settings.LOGIN_URL)
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # expose the user in the template context (TemplateView already provides request via context processors)
        context['user'] = self.request.user
        return context
