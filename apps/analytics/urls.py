from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('hr/', views.HRHubView.as_view(), name='hr_hub'),
    path('hr/candidates/', views.CandidatesView.as_view(), name='candidates'),
    path('hr/visibility/', views.VisibilityView.as_view(), name='visibility'),
    path('hr/comments/', views.CommentModerationView.as_view(), name='comment_moderation'),
    path('hr/onboarding-feedback/', views.OnboardingFeedbackModerationView.as_view(), name='onboarding_feedback_moderation'),
    path('content-review/', views.ContentReviewView.as_view(), name='content_review'),
]
