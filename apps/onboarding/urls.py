from django.urls import path
from . import views

app_name = 'onboarding'
urlpatterns = [
    path('', views.OverviewView.as_view(), name='overview'),
    path('steps/<int:step_id>/complete/', views.MarkStepCompleteView.as_view(), name='mark_step_complete'),
    path('<slug:slug>/', views.ModuleDetailView.as_view(), name='module_detail'),
]
