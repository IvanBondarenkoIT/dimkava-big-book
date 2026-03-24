"""Dim Kava — URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from apps.accounts.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', RedirectView.as_view(url='/login/', permanent=False), name='logout'),
    path('profile/', include('apps.accounts.urls')),
    path('onboarding/', include('apps.onboarding.urls')),
    path('courses/', include('apps.courses.urls')),
    path('wiki/', include('apps.knowledge_base.urls')),
    path('news/', include('apps.news.urls')),
    path('departments/', include('apps.departments.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('search/', include('apps.search.urls')),
]
