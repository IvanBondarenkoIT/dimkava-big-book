from django.urls import path
from . import views

app_name = 'knowledge_base'
urlpatterns = [
    path('', views.KnowledgeBaseHomeView.as_view(), name='home'),
    path('<slug:section>/', views.SectionView.as_view(), name='section'),
    path('<slug:section>/<slug:slug>/', views.ArticleView.as_view(), name='article'),
]
