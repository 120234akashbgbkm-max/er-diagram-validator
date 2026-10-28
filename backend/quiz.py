"""quiz.py - AI-generated quiz, with a built-in fallback if the AI is unavailable."""

import random

from llm import generate_json
from question_bank import QUESTIONS

TOPIC = (
    "ER diagrams and relational database design: entities, attributes (simple, composite, "
    "multivalued, derived), keys, relationships, cardinality and participation, weak entities, "
    "specialization/generalization, ER-to-relational mapping, foreign keys, normalization "
    "(1NF, 2NF, 3NF, BCNF) and common ER design errors"
)

SYSTEM_PROMPT = """You write multiple-choice quiz questions for university students.
Respond with ONLY a JSON array. Each item must be:
{
  "question": "the question text",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_index": 0,
  "explanation": "a clear explanation of why the correct option is right"
}
Rules: exactly 4 options, exactly one correct, correct_index is 0-3, no duplicate questions."""

DIFFICULTY_HINT = {
    "Easy": "Easy: definitions and direct recall.",
    "Medium": "Medium: applying concepts to small scenarios or ER-to-table mapping.",
    "Hard": "Hard: multi-step reasoning, such as functional dependencies, candidate keys, normal forms and counting tables.",
}


def _clean(items):
    out = []
    for it in items if isinstance(items, list) else []:
        try:
            opts = [str(o) for o in it["options"]]
            idx = int(it["correct_index"])
            if len(opts) == 4 and 0 <= idx < 4 and str(it["question"]).strip():
                out.append({
                    "question": str(it["question"]).strip(),
                    "options": opts,
                    "correct_index": idx,
                    "explanation": str(it.get("explanation", "")).strip(),
                })
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _from_bank(count, difficulty):
    same = [q for q in QUESTIONS if q["difficulty"] == difficulty]
    other = [q for q in QUESTIONS if q["difficulty"] != difficulty]
    random.shuffle(same)
    random.shuffle(other)
    chosen = (same + other)[:count]
    return [{
        "question": q["question"],
        "options": q["options"],
        "correct_index": q["answer"],
        "explanation": q["explanation"],
    } for q in chosen]


def generate_quiz(count: int, difficulty: str):
    """Returns (questions, source) where source is 'ai' or 'bank'."""
    user_message = (
        f"Topic: {TOPIC}.\n"
        f"Write exactly {count} multiple-choice questions.\n"
        f"Difficulty: {DIFFICULTY_HINT.get(difficulty, difficulty)}"
    )
    try:
        questions = _clean(generate_json(SYSTEM_PROMPT, user_message))[:count]
        if questions:
            return questions, "ai"
    except Exception:  # noqa: BLE001 - any AI failure falls back to the bank
        pass
    return _from_bank(count, difficulty), "bank"
