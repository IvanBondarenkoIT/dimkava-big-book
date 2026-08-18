"""Tests for quiz grading and HR review breakdown."""
from django.test import TestCase

from .models import Course, Lesson, TestQuestion, UserProgress
from .quiz_review import build_quiz_review_rows, grade_quiz_submission
from .services import save_quiz_result
from django.contrib.auth import get_user_model

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
            options_en=[
                {'text': 'Wrong', 'is_correct': False},
                {'text': 'Right', 'is_correct': True},
            ],
            order=0,
        )
        self.q2 = TestQuestion.objects.create(
            lesson=self.lesson,
            question_text='Q2',
            question_text_en='Q2 EN',
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
