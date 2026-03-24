"""Notifications tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.courses.models import Course, Lesson
from apps.courses.services import mark_lesson_complete, save_quiz_result
from apps.notifications.models import Notification

User = get_user_model()


class NotificationTriggersTest(TestCase):
    """Test that notifications are created on lesson_completed and quiz_passed."""

    def setUp(self):
        self.user = User.objects.create_user(username='u@test.ge', password='pass')
        self.course = Course.objects.create(slug='c1', title='C1', status='published')
        self.lesson = Lesson.objects.create(
            course=self.course, title='L1', order=1, lesson_type='text'
        )
        self.quiz = Lesson.objects.create(
            course=self.course, title='Quiz', order=2, lesson_type='quiz',
            passing_score=70,
        )

    def test_lesson_completed_creates_notification(self):
        before = Notification.objects.count()
        mark_lesson_complete(self.user, self.lesson)
        after = Notification.objects.count()
        self.assertEqual(after, before + 1)
        n = Notification.objects.latest('created_at')
        self.assertEqual(n.user, self.user)
        self.assertEqual(n.type, 'lesson_completed')
        self.assertIn(self.lesson.title, n.text)

    def test_quiz_passed_creates_notification(self):
        from apps.courses.models import TestQuestion
        TestQuestion.objects.create(lesson=self.quiz, question_text='Q?', options=[], order=0)
        before = Notification.objects.count()
        save_quiz_result(self.user, self.quiz, 80, 70)
        after = Notification.objects.count()
        self.assertEqual(after, before + 1)
        n = Notification.objects.latest('created_at')
        self.assertEqual(n.type, 'quiz_passed')
        self.assertIn('80', n.text)
