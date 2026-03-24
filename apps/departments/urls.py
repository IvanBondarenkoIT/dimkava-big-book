from django.urls import path
from . import views

app_name = 'departments'
urlpatterns = [
    path('', views.DepartmentListView.as_view(), name='list'),
    path('<slug:slug>/', views.DepartmentDetailView.as_view(), name='detail'),
]
