from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.knowledge_base.models import KBSection

User = get_user_model()


class KnowledgeBaseAccessTests(TestCase):
    def setUp(self):
        self.section = KBSection.objects.create(slug='procedures', title='Procedures')

    def test_section_requires_login(self):
        r = self.client.get(reverse('knowledge_base:section', kwargs={'section': self.section.slug}))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/login/', r['Location'])

