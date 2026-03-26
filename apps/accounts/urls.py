from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register/candidate/', views.CandidateRegisterView.as_view(), name='register_candidate'),
    path('accounts/confirm-email/', views.ConfirmEmailView.as_view(), name='confirm_email'),
    path('accounts/email-pending/', views.EmailPendingView.as_view(), name='email_pending'),
    path('accounts/resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
]
