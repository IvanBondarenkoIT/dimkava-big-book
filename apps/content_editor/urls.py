from django.urls import path

from apps.content_editor import views

app_name = 'content_editor'

urlpatterns = [
    path('wiki/new/', views.ArticleCreateView.as_view(), name='article_create'),
    path('wiki/<slug:section>/<slug:slug>/', views.ArticleEditView.as_view(), name='article_edit'),
    path('courses/new/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<slug:slug>/', views.CourseEditView.as_view(), name='course_edit'),
    path(
        'courses/<slug:course_slug>/lessons/new/',
        views.LessonCreateView.as_view(),
        name='lesson_create',
    ),
    path(
        'courses/<slug:course_slug>/quizzes/new/',
        views.QuizCreateView.as_view(),
        name='quiz_create',
    ),
    path('lessons/<int:pk>/', views.LessonEditView.as_view(), name='lesson_edit'),
    path(
        'courses/<slug:course_slug>/lessons/<int:pk>/quiz/',
        views.QuizEditView.as_view(),
        name='quiz_edit',
    ),
    path(
        'courses/<slug:course_slug>/lessons/<int:pk>/quiz/questions/new/',
        views.QuizQuestionAddView.as_view(),
        name='quiz_question_add',
    ),
    path('news/new/', views.NewsCreateView.as_view(), name='news_create'),
    path('news/<slug:slug>/', views.NewsEditView.as_view(), name='news_edit'),
    path(
        'onboarding/programs/<slug:slug>/',
        views.OnboardingProgramEditView.as_view(),
        name='onboarding_program_edit',
    ),
    path(
        'onboarding/modules/<int:pk>/',
        views.OnboardingModuleEditView.as_view(),
        name='onboarding_module_edit',
    ),
    path(
        'onboarding/steps/<int:pk>/',
        views.OnboardingStepEditView.as_view(),
        name='onboarding_step_edit',
    ),
    path('roles/<int:pk>/', views.RoleEditView.as_view(), name='role_edit'),
]
