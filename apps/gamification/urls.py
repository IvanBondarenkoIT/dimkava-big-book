from django.urls import path

from . import views

app_name = 'gamification'
urlpatterns = [
    path('', views.GamificationDashboardView.as_view(), name='dashboard'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]
