from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, TemplateView

from django.contrib.auth.views import LoginView as AuthLoginView

from .forms import CandidatePhoneForm, CandidateRegistrationForm
from .email_verification import unsign_user_id
from .mailing import send_candidate_verification_email

User = get_user_model()


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.is_candidate:
            form = CandidatePhoneForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Phone number updated.')
                return HttpResponseRedirect(reverse('accounts:profile'))
            context = self.get_context_data(**kwargs)
            context['phone_form'] = form
            return self.render_to_response(context)
        return HttpResponseRedirect(reverse('accounts:profile'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_name'] = user.get_full_name() or user.username
        context['role'] = _get_role_display(user)
        from apps.courses.selectors import get_active_ilp_context_for_user

        context['ilp'] = get_active_ilp_context_for_user(user)
        profile = user.profile
        context['phone_form'] = CandidatePhoneForm(instance=profile) if profile.is_candidate else None
        context['show_ilp'] = True
        return context


def _get_role_display(user):
    if user.is_superuser:
        return 'Admin'
    if user.groups.filter(name='hr_manager').exists():
        return 'HR / Director'
    if getattr(user.profile, 'is_candidate', False):
        return 'Candidate'
    if user.groups.filter(name='employee').exists():
        return 'Employee'
    return 'User'


class CandidateRegisterView(FormView):
    template_name = 'accounts/register_candidate.html'
    form_class = CandidateRegistrationForm
    success_url = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        phone = form.cleaned_data['phone']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        profile = user.profile
        profile.user_type = 'candidate'
        profile.phone = phone
        profile.email_verified_at = None
        profile.save()
        send_candidate_verification_email(self.request, user)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.info(
            self.request,
            'We sent a confirmation link to your email (optional). You can start learning now.',
        )
        return super().form_valid(form)


class ConfirmEmailView(View):
    """One-click verify from email link (?token=...)."""

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            messages.error(request, 'Invalid confirmation link.')
            return redirect('login')

        uid = unsign_user_id(token)
        if uid is None:
            messages.error(request, 'This confirmation link is invalid or has expired.')
            return redirect('login')

        user = User.objects.filter(pk=uid).first()
        if not user:
            messages.error(request, 'User not found.')
            return redirect('login')

        profile = user.profile
        profile.email_verified_at = timezone.now()
        profile.save(update_fields=['email_verified_at'])
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Email confirmed. Welcome!')
        return redirect('core:home')


class EmailPendingView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/email_pending.html'

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        if not profile.is_candidate:
            return redirect('core:home')
        if profile.email_verified_at:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class ResendVerificationView(LoginRequiredMixin, View):
    http_method_names = ['post', 'options']
    def post(self, request):
        profile = request.user.profile
        if not profile.is_candidate or profile.email_verified_at:
            return redirect('core:home')
        send_candidate_verification_email(request, request.user)
        messages.success(request, 'Verification email sent. Check your inbox.')
        return redirect('accounts:email_pending')
