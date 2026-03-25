"""Courses tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Course, ILPItem, IndividualLearningPlan, Lesson, UserProgress
from .services import mark_lesson_complete, save_quiz_result
from .selectors import get_active_ilp_context_for_user

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


class CandidateVisibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate = User.objects.create_user(username='cand@test.ge', password='pass')
        self.candidate.profile.user_type = 'candidate'
        self.candidate.profile.save()

        self.employee = User.objects.create_user(username='emp@test.ge', password='pass')

        self.public_course = Course.objects.create(slug='c1', title='C1', status='published', level='beginner', visible_for_candidates=True)
        self.private_course = Course.objects.create(slug='c2', title='C2', status='published', level='beginner', visible_for_candidates=False)

        self.public_lesson = Lesson.objects.create(
            course=self.public_course,
            title='L1',
            order=1,
            lesson_type='quiz',
            passing_score=70,
            visible_for_candidates=True,
        )
        Lesson.objects.create(
            course=self.private_course,
            title='L2',
            order=1,
            lesson_type='text',
            estimated_minutes=5,
            visible_for_candidates=False,
        )

    def test_candidate_course_list_filters_out_private(self):
        self.client.login(username='cand@test.ge', password='pass')
        r = self.client.get(reverse('courses:list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'C1')
        self.assertNotContains(r, 'C2')

    def test_candidate_quiz_404_when_not_visible(self):
        self.client.login(username='cand@test.ge', password='pass')
        r = self.client.get(reverse('courses:quiz', kwargs={'slug': self.private_course.slug, 'pk': 999}))
        self.assertIn(r.status_code, (404, 302))


class ILPSelectorsTests(TestCase):
    def test_active_ilp_context_progress_and_next_up(self):
        user = User.objects.create_user(username='ilp@test.ge', password='pass')
        plan = IndividualLearningPlan.objects.create(user=user, title='Plan A', is_active=True)
        ILPItem.objects.create(plan=plan, content_type='course', object_slug='espresso-basics', title='Course 1', order=1, is_completed=True)
        ILPItem.objects.create(plan=plan, content_type='article', object_slug='daily-check', title='Article 1', order=2, is_completed=False)

        ctx = get_active_ilp_context_for_user(user)
        self.assertTrue(ctx['has_plan'])
        self.assertEqual(ctx['progress'], 50)
        self.assertEqual(ctx['next_up']['title'], 'Article 1')
