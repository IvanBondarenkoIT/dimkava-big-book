"""Courses tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import Course, ILPItem, IndividualLearningPlan, Lesson, LessonRating, TestQuestion, UserProgress
from .services import mark_lesson_complete, save_quiz_result, unlock_candidate_quiz_retake
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
        self.candidate.profile.email_verified_at = timezone.now()
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

    def test_candidate_quiz_single_attempt_locked_until_hr_unlock(self):
        from .models import TestQuestion

        q = TestQuestion.objects.create(
            lesson=self.public_lesson,
            question_text='Q1',
            options=[
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False},
            ],
            order=1,
        )
        self.client.login(username='cand@test.ge', password='pass')
        url = reverse('courses:quiz', kwargs={'slug': self.public_course.slug, 'pk': self.public_lesson.pk})
        data = {f'q_{q.pk}': '0'}

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 302)
        p = UserProgress.objects.get(user=self.candidate, lesson=self.public_lesson)
        self.assertTrue(p.candidate_quiz_locked)
        first_score = p.quiz_score

        # Candidate cannot resubmit while locked.
        r = self.client.post(url, data, follow=True)
        self.assertEqual(r.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.quiz_score, first_score)
        self.assertEqual(p.quiz_attempts_count, 1)

        # HR unlocks retake.
        hr = User.objects.create_user(username='hrunlock@test.ge', password='pass')
        unlock_candidate_quiz_retake(p, by_user=hr)
        p.refresh_from_db()
        self.assertFalse(p.candidate_quiz_locked)

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertTrue(p.candidate_quiz_locked)
        self.assertEqual(p.quiz_attempts_count, 2)

    def test_employee_quiz_locked_and_tracks_attempts(self):
        from .models import TestQuestion

        emp_course = Course.objects.create(
            slug='emp-quiz', title='Emp quiz course', status='published', level='beginner',
        )
        quiz = Lesson.objects.create(
            course=emp_course, title='Emp Q', order=1, lesson_type='quiz', passing_score=70,
        )
        q = TestQuestion.objects.create(
            lesson=quiz,
            question_text='Q1',
            options=[
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False},
            ],
            order=1,
        )
        self.client.login(username='emp@test.ge', password='pass')
        url = reverse('courses:quiz', kwargs={'slug': emp_course.slug, 'pk': quiz.pk})
        data = {f'q_{q.pk}': '0'}

        self.client.post(url, data)
        p = UserProgress.objects.get(user=self.employee, lesson=quiz)
        self.assertTrue(p.candidate_quiz_locked)
        self.assertEqual(p.quiz_attempts_count, 1)

        r = self.client.post(url, data, follow=True)
        self.assertEqual(r.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.quiz_attempts_count, 1)


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


class LessonRatingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rate@test.ge', password='pass')
        self.course = Course.objects.create(slug='r1', title='R1', status='published', level='beginner')
        self.lesson = Lesson.objects.create(course=self.course, title='L1', order=1, lesson_type='text', estimated_minutes=5)

    def test_post_rating_creates_or_updates(self):
        self.client.login(username='rate@test.ge', password='pass')
        url = reverse('courses:rate_lesson', kwargs={'slug': self.course.slug, 'pk': self.lesson.pk})
        r = self.client.post(url, {'rating': '4', 'comment': 'Nice'})
        self.assertEqual(r.status_code, 302)
        lr = LessonRating.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(lr.rating, 4)

        self.client.post(url, {'rating': '5', 'comment': 'Great'})
        lr.refresh_from_db()
        self.assertEqual(lr.rating, 5)
