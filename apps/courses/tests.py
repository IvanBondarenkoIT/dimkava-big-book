"""Courses tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Course, Lesson, UserProgress
from .services import mark_lesson_complete, save_quiz_result

User = get_user_model()


class CourseViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u@test.ge', password='pass')
        self.course = Course.objects.create(
            slug='test', title='Test', status='published', level='beginner'
        )
        self.lesson = Lesson.objects.create(
            course=self.course, title='L1', order=1, lesson_type='text', estimated_minutes=5
        )

    def test_mark_lesson_complete(self):
        created = mark_lesson_complete(self.user, self.lesson)
        self.assertTrue(created)
        prog = UserProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertTrue(prog.is_completed)

    def test_save_quiz_result_passed(self):
        lesson = Lesson.objects.create(
            course=self.course, title='Quiz', order=2, lesson_type='quiz', passing_score=70
        )
        passed = save_quiz_result(self.user, lesson, 80, 70)
        self.assertTrue(passed)
        prog = UserProgress.objects.get(user=self.user, lesson=lesson)
        self.assertEqual(prog.quiz_score, 80)
        self.assertTrue(prog.is_completed)
