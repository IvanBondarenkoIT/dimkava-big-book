"""Comment submit / visibility tests."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from apps.comments.models import Comment
from apps.courses.models import Course

User = get_user_model()


class CommentSubmitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmt@test.ge', password='pass')
        self.hr = User.objects.create_user(username='hr-cmt@test.ge', password='pass')
        self.hr.groups.add(Group.objects.get_or_create(name='hr_manager')[0])
        self.course = Course.objects.create(
            slug='cmt-course', title='C', status='published', level='beginner',
        )

    def test_submit_creates_pending_and_author_sees_it(self):
        self.client.login(username='cmt@test.ge', password='pass')
        detail = reverse('courses:detail', kwargs={'slug': self.course.slug})
        r = self.client.post(
            reverse('comments:submit'),
            {
                'app_label': 'courses',
                'model': 'course',
                'object_id': str(self.course.pk),
                'next': detail,
                'text': 'Nice course',
            },
        )
        self.assertEqual(r.status_code, 302)
        c = Comment.objects.get(user=self.user)
        self.assertEqual(c.status, Comment.Status.PENDING)
        page = self.client.get(detail)
        self.assertContains(page, 'Nice course')
        self.assertContains(page, 'Pending')

    def test_other_user_does_not_see_pending(self):
        Comment.objects.create(
            user=self.user,
            content_type=__import__('django.contrib.contenttypes.models', fromlist=['ContentType']).ContentType.objects.get_for_model(Course),
            object_id=self.course.pk,
            text='Hidden pending',
            status=Comment.Status.PENDING,
        )
        other = User.objects.create_user(username='other-cmt@test.ge', password='pass')
        self.client.login(username='other-cmt@test.ge', password='pass')
        page = self.client.get(reverse('courses:detail', kwargs={'slug': self.course.slug}))
        self.assertNotContains(page, 'Hidden pending')
