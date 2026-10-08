"""Quiz grading and HR review breakdown."""
from __future__ import annotations

from dataclasses import dataclass


def canonical_options(question) -> list[dict]:
    """Answer-key source of truth (language-independent)."""
    return question.options_en or question.options or []


def display_options(question) -> list[dict]:
    """Localized option texts for UI; length aligned to canonical list."""
    canonical = canonical_options(question)
    localized = question.localized_options or question.options_en or question.options or []
    out: list[dict] = []
    for i, canon in enumerate(canonical):
        loc = localized[i] if i < len(localized) else {}
        text = (loc.get('text') if isinstance(loc, dict) else '') or canon.get('text', '')
        out.append({'text': text, 'is_correct': bool(canon.get('is_correct'))})
    return out


def question_options(question) -> list[dict]:
    """Backward-compatible alias for display options."""
    return display_options(question)


def answer_key(question) -> set[int]:
    """Indices marked correct in the canonical option list."""
    return {
        i
        for i, opt in enumerate(canonical_options(question))
        if opt.get('is_correct')
    }


def has_answer_key(question) -> bool:
    """False when no correct option, or every option is marked correct (degenerate)."""
    opts = canonical_options(question)
    if not opts:
        return False
    key = answer_key(question)
    if not key:
        return False
    if len(key) == len(opts):
        return False
    return True


def effective_passing_score(lesson) -> int:
    """None → 70; keep explicit 0 as a survey / always-pass mark."""
    if lesson.passing_score is None:
        return 70
    return int(lesson.passing_score)


def grade_quiz_submission(lesson, post) -> tuple[int | None, dict[str, int | None]]:
    """Score 0–100 (or None if no gradable questions) and map qid → selected index."""
    answers: dict[str, int | None] = {}
    correct = 0
    gradable = 0
    questions = list(lesson.questions.all().order_by('order'))
    for q in questions:
        key = f'q_{q.id}'
        val = post.get(key)
        selected = int(val) if val is not None and str(val).isdigit() else None
        answers[str(q.id)] = selected
        if not has_answer_key(q):
            continue
        gradable += 1
        if selected is None:
            continue
        if selected in answer_key(q):
            correct += 1
    if gradable == 0:
        return None, answers
    score = int(round((correct / gradable) * 100))
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
    has_key: bool
    is_answered: bool


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
        options_raw = display_options(q)
        key_idxs = answer_key(q)
        keyed = has_answer_key(q)
        selected_idx = stored.get(q.id)
        if selected_idx is not None:
            try:
                selected_idx = int(selected_idx)
            except (TypeError, ValueError):
                selected_idx = None

        correct_texts = [
            options_raw[i].get('text', '')
            for i in sorted(key_idxs)
            if i < len(options_raw)
        ]
        correct_text = ' / '.join(t for t in correct_texts if t)

        selected_text = None
        if selected_idx is not None and 0 <= selected_idx < len(options_raw):
            selected_text = options_raw[selected_idx].get('text', '')

        is_correct = None
        if keyed and selected_idx is not None:
            is_correct = selected_idx in key_idxs

        option_rows = [
            QuizReviewOption(
                text=opt.get('text', ''),
                is_correct=i in key_idxs if keyed else False,
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
                has_key=keyed,
                is_answered=selected_idx is not None,
            )
        )
    return rows


def summarize_review_rows(rows: list[QuizReviewRow]) -> dict[str, int]:
    """Counters for HR detail header."""
    return {
        'question_count': len(rows),
        'answered_count': sum(1 for r in rows if r.is_answered),
        'unanswered_count': sum(1 for r in rows if not r.is_answered),
        'correct_count': sum(1 for r in rows if r.is_correct is True),
        'wrong_count': sum(1 for r in rows if r.is_correct is False),
        'missing_key_count': sum(1 for r in rows if not r.has_key),
    }
