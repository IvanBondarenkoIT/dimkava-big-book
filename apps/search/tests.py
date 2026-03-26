"""Tests for global search."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.courses.models import Course, Lesson
from apps.departments.models import Department, Role
from apps.knowledge_base.models import Article, KBSection
from apps.news.models import NewsPost
from apps.search.selectors import global_search

User = get_user_model()


class GlobalSearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="test")

    def test_empty_query_returns_nothing(self):
        self.assertEqual(global_search("", self.user), [])
        self.assertEqual(global_search("   ", self.user), [])

    def test_search_courses(self):
        Course.objects.create(
            title="Coffee Basics",
            slug="coffee-basics",
            description="Learn coffee fundamentals",
            status="published",
        )
        results = global_search("coffee", self.user)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, "course")
        self.assertEqual(results[0].title, "Coffee Basics")
        self.assertIn("coffee-basics", results[0].url)

    def test_search_excludes_draft_courses(self):
        Course.objects.create(
            title="Secret Course",
            slug="secret",
            status="draft",
        )
        results = global_search("secret", self.user)
        self.assertEqual(len(results), 0)

    def test_search_articles(self):
        section = KBSection.objects.create(slug="proc", title="Procedures", order=0)
        Article.objects.create(
            section=section,
            slug="brewing",
            title="Brewing Guide",
            content="How to brew perfect coffee",
            status="published",
        )
        results = global_search("brewing", self.user)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, "article")
        self.assertIn("brewing", results[0].url)

    def test_search_news(self):
        from django.utils import timezone

        NewsPost.objects.create(
            slug="announcement",
            title="New Barista Training",
            content="Join our barista program",
            published_at=timezone.now(),
        )
        results = global_search("barista", self.user)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, "news")

    def test_search_roles(self):
        dept = Department.objects.create(name="Retail", slug="retail")
        Role.objects.create(
            title="Barista",
            department=dept,
            description="Coffee preparation specialist",
            order=0,
        )
        results = global_search("barista", self.user)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, "role")
        self.assertEqual(results[0].department, "Retail")

    def test_candidate_search_filters_to_candidate_visible_only(self):
        candidate = User.objects.create_user(username="cand", password="test")
        candidate.profile.user_type = 'candidate'
        candidate.profile.save()

        Course.objects.create(
            title="Public Coffee",
            slug="public-coffee",
            description="Public",
            status="published",
            visible_for_candidates=True,
        )
        Course.objects.create(
            title="Private Coffee",
            slug="private-coffee",
            description="Private",
            status="published",
            visible_for_candidates=False,
        )
        results = global_search("coffee", candidate)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, "course")
        self.assertIn("public-coffee", results[0].url)
