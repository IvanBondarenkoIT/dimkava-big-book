from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('content-review/', views.ContentReviewView.as_view(), name='content_review'),
]
