"""Onboarding tests."""
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse

from .models import Mentor, MentorAssignment, MentorSession, OnboardingFeedback, OnboardingProgram, OnboardingModule, OnboardingStep, OnboardingProgress
from .services import mark_step_complete

User = get_user_model()


class OnboardingModelsTest(TestCase):
    def test_create_program_module_step(self):
        program = OnboardingProgram.objects.create(
            slug='test-prog', title='Test Program', estimated_days=30
        )
        module = OnboardingModule.objects.create(
            program=program, slug='day-1', title='Day 1', order=1, estimated_minutes=60
        )
        step = OnboardingStep.objects.create(
            module=module, order=1, title='Step 1', content='Content'
        )
        self.assertEqual(program.modules.count(), 1)
        self.assertEqual(module.steps.count(), 1)


class MarkStepCompleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u@test.ge', password='pass')
        self.program = OnboardingProgram.objects.create(
            slug='p', title='P', estimated_days=7
        )
        self.module = OnboardingModule.objects.create(
            program=self.program, slug='m1', title='M1', order=1, estimated_minutes=30
        )
        self.step = OnboardingStep.objects.create(
            module=self.module, order=1, title='S1', content=''
        )

    def test_mark_step_complete_creates_progress(self):
        created = mark_step_complete(self.user, self.step)
        self.assertTrue(created)
        self.assertEqual(OnboardingProgress.objects.filter(user=self.user, step=self.step).count(), 1)

    def test_mark_step_complete_idempotent(self):
        mark_step_complete(self.user, self.step)
        created = mark_step_complete(self.user, self.step)
        self.assertFalse(created)
        self.assertEqual(OnboardingProgress.objects.filter(user=self.user, step=self.step).count(), 1)


class LoadOnboardingCommandTest(TestCase):
    def test_load_onboarding_creates_data(self):
        out = StringIO()
        call_command('load_onboarding', stdout=out)
        self.assertGreater(OnboardingProgram.objects.count(), 0)
        self.assertGreater(OnboardingModule.objects.count(), 0)
        self.assertGreater(OnboardingStep.objects.count(), 0)


class MarkStepCompleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u@test.ge', password='pass')
        self.program = OnboardingProgram.objects.create(slug='p', title='P', estimated_days=7)
        self.module = OnboardingModule.objects.create(
            program=self.program, slug='m1', title='M1', order=1, estimated_minutes=30
        )
        self.step = OnboardingStep.objects.create(module=self.module, order=1, title='S1', content='')

    def test_post_marks_complete_and_redirects(self):
        self.client.login(username='u@test.ge', password='pass')
        r = self.client.post(reverse('onboarding:mark_step_complete', args=[self.step.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn(self.module.slug, r.url)
        self.assertEqual(OnboardingProgress.objects.filter(user=self.user, step=self.step).count(), 1)


class MentorBlockTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.mentor_user = User.objects.create_user(username='mentor@test.ge', password='pass')
        self.mentee = User.objects.create_user(username='mentee@test.ge', password='pass')
        self.program = OnboardingProgram.objects.create(slug='p', title='P', estimated_days=7)
        OnboardingModule.objects.create(program=self.program, slug='m1', title='M1', order=1, estimated_minutes=30)

    def test_overview_hides_block_without_assignment(self):
        self.client.login(username='mentee@test.ge', password='pass')
        r = self.client.get(reverse('onboarding:overview'))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'Your Mentor')

    def test_overview_shows_block_with_active_mentor(self):
        mentor = Mentor.objects.create(
            user=self.mentor_user,
            title='Senior Barista',
            contact_info='Slack: @mentor',
            responsibility_area='Espresso',
            is_active=True,
        )
        assignment = MentorAssignment.objects.create(mentee=self.mentee, mentor=mentor)
        MentorSession.objects.create(assignment=assignment, session_type='day_1', scheduled_date='2026-03-25')

        self.client.login(username='mentee@test.ge', password='pass')
        r = self.client.get(reverse('onboarding:overview'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Your Mentor')
        self.assertContains(r, 'Senior Barista')


class OnboardingFeedbackTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='fb@test.ge', password='pass')
        self.program = OnboardingProgram.objects.create(slug='p', title='P', estimated_days=7)
        OnboardingModule.objects.create(program=self.program, slug='m1', title='M1', order=1, estimated_minutes=30)

    def test_submit_feedback_creates_record(self):
        self.client.login(username='fb@test.ge', password='pass')
        r = self.client.post(reverse('onboarding:submit_feedback'), {'rating': '5', 'comment': 'Great'})
        self.assertEqual(r.status_code, 302)
        fb = OnboardingFeedback.objects.get(user=self.user, program=self.program)
        self.assertEqual(fb.rating, 5)
        self.assertEqual(fb.comment, 'Great')
