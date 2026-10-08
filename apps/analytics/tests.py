"""Analytics tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.analytics.selectors import get_analytics_metrics

User = get_user_model()


class AnalyticsSelectorsTests(TestCase):
    """Unit tests for analytics selectors."""

    def test_get_analytics_metrics_empty(self):
        """Metrics with no data."""
        m = get_analytics_metrics()
        self.assertEqual(m['active_courses'], 0)
        self.assertEqual(m['onboarding_in_progress'], 0)
        self.assertEqual(m['onboarding_completion_rate'], 0)
        self.assertIsNone(m['avg_onboarding_days'])
        self.assertEqual(m['course_completion_rate'], 0)
        self.assertEqual(m['total_users'], 0)

    def test_get_analytics_metrics_with_courses(self):
        """Active courses count."""
        from apps.courses.models import Course
        Course.objects.create(slug='test', title='Test', status='published')
        Course.objects.create(slug='draft', title='Draft', status='draft')
        m = get_analytics_metrics()
        self.assertEqual(m['active_courses'], 1)


class ContentReviewAccessTests(TestCase):
    def test_hr_can_open_content_review(self):
        hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])

        self.client.login(username='hr@test.local', password='x')
        resp = self.client.get(reverse('analytics:content_review'))
        self.assertEqual(resp.status_code, 200)

    def test_regular_user_cannot_open_content_review(self):
        u = User.objects.create_user(username='u@test.local', password='x')
        self.client.login(username='u@test.local', password='x')
        resp = self.client.get(reverse('analytics:content_review'))
        self.assertEqual(resp.status_code, 403)


class HRHubAccessTests(TestCase):
    def test_hr_can_open_hr_hub_and_candidates(self):
        hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])

        self.client.login(username='hr@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:hr_hub')).status_code, 200)
        self.assertEqual(self.client.get(reverse('analytics:candidates')).status_code, 200)

    def test_regular_user_cannot_open_hr_hub(self):
        u = User.objects.create_user(username='u@test.local', password='x')
        self.client.login(username='u@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:hr_hub')).status_code, 403)


class HRToolsAccessTests(TestCase):
    def setUp(self):
        self.hr = User.objects.create_user(username='hr@test.local', password='x')
        from django.contrib.auth.models import Group
        self.hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])
        self.u = User.objects.create_user(username='u@test.local', password='x')

    def test_hr_can_open_visibility_and_comments(self):
        self.client.login(username='hr@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:visibility')).status_code, 200)
        self.assertEqual(self.client.get(reverse('analytics:comment_moderation')).status_code, 200)
        self.assertEqual(self.client.get(reverse('analytics:onboarding_feedback_moderation')).status_code, 200)

    def test_regular_user_cannot_open_visibility(self):
        self.client.login(username='u@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:visibility')).status_code, 403)

    def test_onboarding_feedback_moderation_filters(self):
        from apps.onboarding.models import OnboardingProgram, OnboardingFeedback

        self.client.login(username='hr@test.local', password='x')
        p1 = OnboardingProgram.objects.create(slug='p1-test', title='P1')
        p2 = OnboardingProgram.objects.create(slug='p2-test', title='P2')
        u1 = User.objects.create_user(username='fb1@test.local', email='fb1@test.local', password='x')
        u2 = User.objects.create_user(username='fb2@test.local', email='fb2@test.local', password='x')
        OnboardingFeedback.objects.create(user=u1, program=p1, rating=5, comment='Great progress')
        OnboardingFeedback.objects.create(user=u2, program=p2, rating=2, comment='Needs support')

        base = reverse('analytics:onboarding_feedback_moderation')
        r = self.client.get(base, {'program': str(p1.id)})
        self.assertContains(r, 'Great progress')
        self.assertNotContains(r, 'Needs support')

        r = self.client.get(base, {'rating': '2'})
        self.assertContains(r, 'Needs support')
        self.assertNotContains(r, 'Great progress')

        r = self.client.get(base, {'q': 'fb1@test.local'})
        self.assertContains(r, 'Great progress')
        self.assertNotContains(r, 'Needs support')


class QuizResultsHRTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        from django.utils import timezone

        from apps.courses.models import Course, Lesson, TestQuestion, UserProgress

        self.hr = User.objects.create_user(username='hr-quiz@test.local', password='x')
        self.hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])
        self.employee = User.objects.create_user(username='emp-quiz@test.local', password='x')
        self.candidate = User.objects.create_user(
            username='cand-quiz@test.local', email='cand-quiz@test.local', password='x'
        )
        self.candidate.profile.user_type = 'candidate'
        self.candidate.profile.save()

        course = Course.objects.create(slug='quiz-hr-course', title='Espresso', status='published')
        self.lesson = Lesson.objects.create(
            course=course, title='Extraction quiz', order=1, lesson_type='quiz', passing_score=70,
        )
        self.question = TestQuestion.objects.create(
            lesson=self.lesson,
            question_text='What is TDS?',
            question_text_en='What is TDS?',
            options_en=[
                {'text': 'Too low', 'is_correct': False},
                {'text': '18-22 percent', 'is_correct': True},
            ],
            order=0,
        )
        UserProgress.objects.create(
            user=self.candidate,
            lesson=self.lesson,
            is_completed=False,
            completed_at=timezone.now(),
            quiz_score=39,
            quiz_attempts_count=1,
            candidate_quiz_locked=True,
            quiz_answers={str(self.question.id): 0},
        )

    def test_employee_cannot_open_quiz_results(self):
        self.client.login(username='emp-quiz@test.local', password='x')
        self.assertEqual(self.client.get(reverse('analytics:quiz_results')).status_code, 403)

    def test_hr_sees_quiz_and_takers(self):
        self.client.login(username='hr-quiz@test.local', password='x')
        list_resp = self.client.get(reverse('analytics:quiz_results'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, 'Extraction quiz')

        takers_url = reverse('analytics:quiz_results_takers', kwargs={'lesson_id': self.lesson.pk})
        takers_resp = self.client.get(takers_url)
        self.assertEqual(takers_resp.status_code, 200)
        self.assertContains(takers_resp, 'cand-quiz@test.local')
        self.assertContains(takers_resp, '39%')

        detail_url = reverse(
            'analytics:quiz_results_detail',
            kwargs={'lesson_id': self.lesson.pk, 'user_id': self.candidate.pk},
        )
        detail_resp = self.client.get(detail_url)
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'What is TDS?')
        self.assertContains(detail_resp, 'Wrong')
        self.assertContains(detail_resp, '18-22 percent')
        self.assertContains(detail_resp, 'Allow retake')

    def test_hr_unlock_retake_for_employee(self):
        from django.utils import timezone
        from apps.courses.models import UserProgress

        UserProgress.objects.create(
            user=self.employee,
            lesson=self.lesson,
            is_completed=False,
            completed_at=timezone.now(),
            quiz_score=55,
            quiz_attempts_count=1,
            candidate_quiz_locked=True,
        )
        self.client.login(username='hr-quiz@test.local', password='x')
        detail_url = reverse(
            'analytics:quiz_results_detail',
            kwargs={'lesson_id': self.lesson.pk, 'user_id': self.employee.pk},
        )
        detail_resp = self.client.get(detail_url)
        self.assertContains(detail_resp, 'Allow retake')

        resp = self.client.post(detail_url, {'action': 'unlock'})
        self.assertEqual(resp.status_code, 302)
        progress = UserProgress.objects.get(user=self.employee, lesson=self.lesson)
        self.assertFalse(progress.candidate_quiz_locked)

    def test_hr_unlock_retake_for_candidate(self):
        from apps.courses.models import UserProgress

        self.client.login(username='hr-quiz@test.local', password='x')
        detail_url = reverse(
            'analytics:quiz_results_detail',
            kwargs={'lesson_id': self.lesson.pk, 'user_id': self.candidate.pk},
        )
        resp = self.client.post(detail_url, {'action': 'unlock'})
        self.assertEqual(resp.status_code, 302)
        progress = UserProgress.objects.get(user=self.candidate, lesson=self.lesson)
        self.assertFalse(progress.candidate_quiz_locked)
        self.assertEqual(progress.quiz_score, 39)

    def test_missing_taker_is_404(self):
        self.client.login(username='hr-quiz@test.local', password='x')
        url = reverse(
            'analytics:quiz_results_detail',
            kwargs={'lesson_id': self.lesson.pk, 'user_id': self.employee.pk},
        )
        self.assertEqual(self.client.get(url).status_code, 404)


class HRTaskStackTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        from apps.comments.models import Comment
        from apps.courses.models import Course, Lesson, UserProgress
        from django.contrib.contenttypes.models import ContentType
        from django.utils import timezone

        self.hr = User.objects.create_user(username='hr-stack@test.local', password='x')
        self.hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])
        self.emp = User.objects.create_user(username='emp-stack@test.local', password='x')
        course = Course.objects.create(slug='stack-c', title='S', status='published')
        Comment.objects.create(
            user=self.emp,
            content_type=ContentType.objects.get_for_model(Course),
            object_id=course.pk,
            text='Please approve',
            status=Comment.Status.PENDING,
        )

    def test_hr_sees_task_stack(self):
        self.client.login(username='hr-stack@test.local', password='x')
        r = self.client.get(reverse('analytics:hr_task_stack'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Please approve')
        hub = self.client.get(reverse('analytics:hr_hub'))
        self.assertContains(hub, 'Task Stack')
