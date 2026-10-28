"""
er_model.py
Turns an "extracted" description of an ER diagram (from the SQL parser or from the AI)
into the same model format the draw.io parser produces, so the validator, the AI review
and the frontend never need to know where the diagram came from.

Extracted format:
{
  "notation": "chen" | "crowsfoot" | "sql" | "other",
  "tables": [{"name": "Orders",
              "columns": [{"name": "order_id", "type": "INT", "keys": ["PK"],
                           "references": "Customer"}]}],      # 'references' is optional
  "relationships": [{"name": "places", "from": "Customer", "to": "Orders",
                     "from_cardinality": "1", "to_cardinality": "0..N"}]
}
"""

import re

# any spelling of a cardinality -> (clean label, is_many)
_CARD = {
    "1": ("1", False), "1..1": ("1", False), "one": ("1", False), "exactlyone": ("1", False),
    "mandatoryone": ("1", False), "onlyone": ("1", False),
    "0..1": ("0..1", False), "zeroorone": ("0..1", False), "optionalone": ("0..1", False),
    "n": ("N", True), "m": ("N", True), "many": ("N", True),
    "1..n": ("1..N", True), "1..m": ("1..N", True), "1..*": ("1..N", True), "oneormany": ("1..N", True),
    "0..n": ("0..N", True), "0..m": ("0..N", True), "0..*": ("0..N", True), "*": ("0..N", True),
    "zeroormany": ("0..N", True),
}


def normalize_card(value):
    """Return (label, is_many); (None, False) when missing or unrecognised."""
    if value is None:
        return None, False
    key = re.sub(r"[\s_-]", "", str(value).strip().lower())
    return _CARD.get(key, (None, False))


def _key_of(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _layout(tables):
    """Place tables on a simple grid so the diagram view can draw them later."""
    per_row, gap_x, gap_y, width = 3, 60, 50, 220
    x_cursor = y_cursor = 40
    row_height = 0
    for i, t in enumerate(tables):
        height = 32 + 26 * max(1, len(t["attributes"]))
        t.update(x=float(x_cursor), y=float(y_cursor), width=float(width), height=float(height))
        row_height = max(row_height, height)
        x_cursor += width + gap_x
        if (i + 1) % per_row == 0:
            x_cursor, y_cursor, row_height = 40, y_cursor + row_height + gap_y, 0


def build_model(extracted):
    tables_in = extracted.get("tables") or []
    entities, by_name = [], {}

    for ti, t in enumerate(tables_in, start=1):
        tid = f"t{ti}"
        cols = []
        for ci, c in enumerate(t.get("columns") or [], start=1):
            keys = {str(k).strip().upper() for k in (c.get("keys") or [])}
            col = {
                "id": f"{tid}_c{ci}",
                "name": str(c.get("name", "")).strip(),
                "type": str(c.get("type") or "").strip(),
                "is_pk": "PK" in keys,
                "is_fk": "FK" in keys or bool(c.get("references")),
                "is_unique": "UK" in keys,
            }
            if c.get("references"):
                col["ref_name"] = str(c["references"]).strip()
            cols.append(col)
        name = str(t.get("name", "")).strip()
        entities.append({"id": tid, "name": name, "attributes": cols})
        by_name.setdefault(_key_of(name), tid)

    _layout(entities)

    relationships = []
    for ri, r in enumerate(extracted.get("relationships") or [], start=1):
        f_label, f_many = normalize_card(r.get("from_cardinality"))
        t_label, t_many = normalize_card(r.get("to_cardinality"))
        relationships.append({
            "id": f"r{ri}",
            "name": str(r.get("name") or "").strip(),
            "from": by_name.get(_key_of(r.get("from"))),
            "to": by_name.get(_key_of(r.get("to"))),
            "from_column": None,
            "to_column": None,
            "from_cardinality": f_label,
            "to_cardinality": t_label,
            "from_many": f_many,
            "to_many": t_many,
        })

    return {
        "entities": entities,
        "relationships": relationships,
        "notation": extracted.get("notation") or "other",
    }
