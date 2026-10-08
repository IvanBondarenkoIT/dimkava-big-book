"""Helpers for creating lessons and quiz questions in the portal editor."""
from django.db.models import Max

from apps.core.i18n_content import sync_question_legacy
from apps.courses.models import Lesson, TestQuestion


def next_lesson_order(course) -> int:
    current = course.lessons.aggregate(m=Max('order')).get('m')
    return (current or 0) + 1


def blank_option_slot(*, is_correct: bool = False) -> dict:
    return {'text': '', 'is_correct': is_correct}


def blank_options(*, correct_index: int | None = None) -> list[dict]:
    """Four empty option slots; optional single correct index for editor radios."""
    options = []
    for i in range(4):
        options.append(blank_option_slot(is_correct=(correct_index is not None and i == correct_index)))
    return options


def next_question_order(lesson: Lesson) -> int:
    current = lesson.questions.aggregate(m=Max('order')).get('m')
    if current is None:
        return 0
    return current + 1


def create_blank_test_question(lesson: Lesson, *, order: int | None = None) -> TestQuestion:
    """Create an empty MC question ready for QuizEditView."""
    if order is None:
        order = next_question_order(lesson)
    opts = blank_options(correct_index=None)
    question = TestQuestion(
        lesson=lesson,
        order=order,
        question_text='',
        question_text_en='',
        question_text_ru='',
        question_text_ka='',
        options=opts,
        options_en=opts,
        options_ru=opts,
        options_ka=opts,
    )
    sync_question_legacy(question)
    question.save()
    return question


def create_blank_quiz_questions(lesson: Lesson, *, count: int = 3) -> list[TestQuestion]:
    created = []
    start = next_question_order(lesson)
    for i in range(count):
        created.append(create_blank_test_question(lesson, order=start + i))
    return created
