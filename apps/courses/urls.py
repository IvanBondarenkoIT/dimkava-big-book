from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<slug:slug>/lessons/<int:pk>/quiz/', views.QuizView.as_view(), name='quiz'),
]
