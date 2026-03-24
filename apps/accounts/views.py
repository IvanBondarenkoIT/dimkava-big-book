from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = 'accounts/login.html'


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_name'] = 'Alex'
        context['role'] = 'Head Barista'
        return context
