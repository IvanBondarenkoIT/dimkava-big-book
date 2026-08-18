"""Quiz grading and HR review breakdown."""
from __future__ import annotations

from dataclasses import dataclass


def question_options(question) -> list[dict]:
    return question.localized_options or question.options_en or question.options or []


def grade_quiz_submission(lesson, post) -> tuple[int, dict[str, int | None]]:
    """Score 0–100 and map question_id (str) → selected option index."""
    answers: dict[str, int | None] = {}
    correct = 0
    questions = list(lesson.questions.all().order_by('order'))
    total = len(questions)
    for q in questions:
        key = f'q_{q.id}'
        val = post.get(key)
        selected = int(val) if val is not None and str(val).isdigit() else None
        answers[str(q.id)] = selected
        if selected is None:
            continue
        options = question_options(q)
        for i, opt in enumerate(options):
            if opt.get('is_correct') and i == selected:
                correct += 1
                break
    score = int((correct / total) * 100) if total else 0
    return score, answers


@dataclass(frozen=True)
class QuizReviewOption:
    text: str
    is_correct: bool
    is_selected: bool


@dataclass(frozen=True)
class QuizReviewRow:
    question_id: int
    order: int
    question_text: str
    is_correct: bool | None
    options: list[QuizReviewOption]
    selected_option_text: str | None
    correct_option_text: str


def build_quiz_review_rows(lesson, quiz_answers: dict | None) -> list[QuizReviewRow]:
    """Build per-question review for HR. quiz_answers keys are str(question_id)."""
    stored = {}
    if quiz_answers:
        for k, v in quiz_answers.items():
            try:
                stored[int(k)] = v
            except (TypeError, ValueError):
                continue

    rows: list[QuizReviewRow] = []
    for q in lesson.questions.all().order_by('order'):
        options_raw = question_options(q)
        selected_idx = stored.get(q.id)
        correct_idx = next(
            (i for i, opt in enumerate(options_raw) if opt.get('is_correct')),
            None,
        )
        correct_text = ''
        if correct_idx is not None and correct_idx < len(options_raw):
            correct_text = options_raw[correct_idx].get('text', '')

        selected_text = None
        if selected_idx is not None and 0 <= selected_idx < len(options_raw):
            selected_text = options_raw[selected_idx].get('text', '')

        is_correct = None
        if selected_idx is not None and correct_idx is not None:
            is_correct = selected_idx == correct_idx

        option_rows = [
            QuizReviewOption(
                text=opt.get('text', ''),
                is_correct=bool(opt.get('is_correct')),
                is_selected=selected_idx is not None and i == selected_idx,
            )
            for i, opt in enumerate(options_raw)
        ]
        rows.append(
            QuizReviewRow(
                question_id=q.id,
                order=q.order,
                question_text=q.localized_question_text,
                is_correct=is_correct,
                options=option_rows,
                selected_option_text=selected_text,
                correct_option_text=correct_text,
            )
        )
    return rows
