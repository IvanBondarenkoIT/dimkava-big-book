"""Tests for quiz grading and HR review breakdown."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import translation

from .models import Course, Lesson, TestQuestion, UserProgress
from .quiz_review import (
    answer_key,
    build_quiz_review_rows,
    effective_passing_score,
    grade_quiz_submission,
    has_answer_key,
    summarize_review_rows,
)
from .services import save_quiz_result

User = get_user_model()


class QuizReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='review@test.ge', password='pass')
        self.course = Course.objects.create(slug='rev', title='Rev', status='published')
        self.lesson = Lesson.objects.create(
            course=self.course, title='Quiz', order=1, lesson_type='quiz', passing_score=70,
        )
        self.q1 = TestQuestion.objects.create(
            lesson=self.lesson,
            question_text='Q1',
            question_text_en='Q1 EN',
            options=[
                {'text': 'Wrong', 'is_correct': False},
                {'text': 'Right', 'is_correct': True},
            ],
            options_en=[
                {'text': 'Wrong', 'is_correct': False},
                {'text': 'Right', 'is_correct': True},
            ],
            options_ru=[
                {'text': 'Неверно', 'is_correct': False},
                {'text': 'Верно', 'is_correct': True},
            ],
            order=0,
        )
        self.q2 = TestQuestion.objects.create(
            lesson=self.lesson,
            question_text='Q2',
            question_text_en='Q2 EN',
            options=[
                {'text': 'Yes', 'is_correct': True},
                {'text': 'No', 'is_correct': False},
            ],
            options_en=[
                {'text': 'Yes', 'is_correct': True},
                {'text': 'No', 'is_correct': False},
            ],
            order=1,
        )

    def test_grade_quiz_submission(self):
        post = {f'q_{self.q1.id}': '1', f'q_{self.q2.id}': '0'}
        score, answers = grade_quiz_submission(self.lesson, post)
        self.assertEqual(score, 100)
        self.assertEqual(answers[str(self.q1.id)], 1)
        self.assertEqual(answers[str(self.q2.id)], 0)

    def test_unanswered_counts_as_wrong(self):
        post = {f'q_{self.q1.id}': '1'}
        score, answers = grade_quiz_submission(self.lesson, post)
        self.assertEqual(score, 50)
        self.assertIsNone(answers[str(self.q2.id)])

    def test_grading_uses_canonical_key_not_ui_language(self):
        # RU list has swapped flags — must still grade by EN/canonical key.
        self.q1.options_ru = [
            {'text': 'Неверно', 'is_correct': True},
            {'text': 'Верно', 'is_correct': False},
        ]
        self.q1.save(update_fields=['options_ru'])
        post = {f'q_{self.q1.id}': '1', f'q_{self.q2.id}': '0'}
        with translation.override('ru'):
            score, _ = grade_quiz_submission(self.lesson, post)
        self.assertEqual(score, 100)

    def test_degenerate_all_correct_has_no_key(self):
        self.q1.options_en = [
            {'text': 'A', 'is_correct': True},
            {'text': 'B', 'is_correct': True},
        ]
        self.q1.options = self.q1.options_en
        self.q1.save()
        self.assertFalse(has_answer_key(self.q1))
        self.assertEqual(answer_key(self.q1), {0, 1})

    def test_effective_passing_score_keeps_zero(self):
        self.lesson.passing_score = 0
        self.assertEqual(effective_passing_score(self.lesson), 0)
        self.lesson.passing_score = None
        self.assertEqual(effective_passing_score(self.lesson), 70)

    def test_save_quiz_result_stores_answers(self):
        answers = {str(self.q1.id): 0, str(self.q2.id): 0}
        save_quiz_result(self.user, self.lesson, 50, 70, quiz_answers=answers)
        prog = UserProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(prog.quiz_answers[str(self.q1.id)], 0)
        self.assertIsNotNone(prog.completed_at)

    def test_build_quiz_review_rows_marks_wrong_and_correct(self):
        rows = build_quiz_review_rows(
            self.lesson,
            {str(self.q1.id): 0, str(self.q2.id): 0},
        )
        self.assertEqual(len(rows), 2)
        self.assertFalse(rows[0].is_correct)
        self.assertTrue(rows[1].is_correct)
        self.assertEqual(rows[0].correct_option_text, 'Right')
        self.assertEqual(rows[0].selected_option_text, 'Wrong')
        summary = summarize_review_rows(rows)
        self.assertEqual(summary['correct_count'], 1)
        self.assertEqual(summary['wrong_count'], 1)
        self.assertEqual(summary['answered_count'], 2)
        self.assertEqual(summary['unanswered_count'], 0)

    def test_review_counts_unanswered(self):
        rows = build_quiz_review_rows(self.lesson, {str(self.q1.id): 1})
        summary = summarize_review_rows(rows)
        self.assertEqual(summary['answered_count'], 1)
        self.assertEqual(summary['unanswered_count'], 1)
        self.assertEqual(summary['correct_count'], 1)
        self.assertTrue(rows[1].is_answered is False)
