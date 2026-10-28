"""ai_review.py - AI pass over the parsed ER diagram (semantic checks)."""

from llm import generate_json

SYSTEM_PROMPT = """You are an expert database designer reviewing an ER diagram.
You receive the diagram as JSON plus the issues a rule-based checker already found.

Find problems the rules CANNOT catch, such as:
- poor or inconsistent naming
- normalization problems (1NF/2NF/3NF), e.g. repeating groups, derived or redundant attributes
- many-to-many relationships that should be resolved with a junction entity
- cardinalities that don't make sense for the domain
- entities that are likely missing, or attributes placed on the wrong entity
- relationships that don't make sense between the entities they connect

Do NOT repeat issues the rule-based checker already reported.
Do NOT comment on indexing, performance, or physical implementation. Only review the logical design.
Only reference element ids that actually appear in the diagram JSON.

Respond with ONLY a JSON array. Each item:
{
  "severity": "error" or "warning",
  "type": "SHORT_UPPER_SNAKE_CASE_NAME",
  "message": "what is wrong, in one or two sentences",
  "suggestion": "how to fix it",
  "element_ids": ["ids of the shapes involved"]
}
If you find nothing, respond with []."""


def _collect_ids(obj, found=None):
    if found is None:
        found = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if (key == "id" or key.endswith("_id")) and isinstance(value, (str, int)):
                found.add(str(value))
            _collect_ids(value, found)
    elif isinstance(obj, list):
        for item in obj:
            _collect_ids(item, found)
    return found


def review_with_ai(diagram: dict, rule_results: dict) -> list:
    import json

    user_message = (
        "DIAGRAM:\n" + json.dumps(diagram, indent=1)
        + "\n\nISSUES ALREADY FOUND BY RULES:\n" + json.dumps(rule_results, indent=1)
    )
    issues = generate_json(SYSTEM_PROMPT, user_message)
    if not isinstance(issues, list):
        issues = []

    valid_ids = _collect_ids(diagram)
    cleaned = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue["element_ids"] = [i for i in issue.get("element_ids", []) if str(i) in valid_ids]
        issue["source"] = "ai"
        cleaned.append(issue)
    return cleaned
