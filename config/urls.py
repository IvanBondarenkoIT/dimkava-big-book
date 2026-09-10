"""Dim Kava — URL Configuration"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.utils.translation import gettext_lazy as _

from apps.accounts.views import LoginView

admin.site.site_header = _('Dim Kava Admin')
admin.site.site_title = _('Dim Kava Admin')
admin.site.index_title = _('Administration')

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/password-reset/done/',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/password-reset/complete/',
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
    path('', include('apps.accounts.urls')),
    path('onboarding/', include('apps.onboarding.urls')),
    path('courses/', include('apps.courses.urls')),
    path('wiki/', include('apps.knowledge_base.urls')),
    path('news/', include('apps.news.urls')),
    path('departments/', include('apps.departments.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('search/', include('apps.search.urls')),
    path('edit/', include('apps.content_editor.urls')),
    path('gamification/', include('apps.gamification.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('comments/', include('apps.comments.urls')),
]
