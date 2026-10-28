"""
er_validator.py
Deterministic rule checks on the model produced by er_parser.parse_drawio.
Returns {errors, warnings, error_count, warning_count}; every issue carries
element_ids (table / column / edge ids) so the UI can highlight them later.
"""

from collections import defaultdict


def _norm(name):
    """'Orders' / 'order' / 'Categories' / 'category' -> comparable stem."""
    n = "".join(ch for ch in (name or "").lower() if ch.isalnum())
    if n.endswith("ies") and len(n) > 3:
        return n[:-3] + "y"
    if n.endswith("s") and not n.endswith("ss") and len(n) > 2:
        return n[:-1]
    return n


def _fk_stem(col_name):
    n = (col_name or "").lower()
    for suffix in ("_id", "id", "_fk", "_key", "_code"):
        if n.endswith(suffix) and len(n) > len(suffix):
            return _norm(n[: -len(suffix)])
    return _norm(n)


def _issue(kind, message, ids):
    return {"type": kind, "message": message, "element_ids": [i for i in ids if i]}


def _resolve_fk(fk_col, owner, tables):
    """Which table does this FK column point to? An explicit REFERENCES target (from SQL or
    AI extraction) wins. Otherwise try a PK-name match, then the column-name stem."""
    if fk_col.get("ref_name"):
        wanted = fk_col["ref_name"].strip().lower()
        for t in tables:
            if t["name"].strip().lower() == wanted:
                return t
        return None
    for t in tables:
        if t["id"] == owner["id"]:
            continue
        if any(c["is_pk"] and c["name"].lower() == fk_col["name"].lower()
               for c in t["attributes"]):
            return t
    stem = _fk_stem(fk_col["name"])
    for t in tables:
        if t["id"] != owner["id"] and _norm(t["name"]) == stem:
            return t
    return None


def validate(model):
    tables = model["entities"]
    rels = model["relationships"]
    by_id = {t["id"]: t for t in tables}
    errors, warnings = [], []

    # Only flag a missing data type if the diagram shows types somewhere; many diagrams
    # (Chen notation, photos) legitimately show none, and warning on every column is noise.
    diagram_has_types = any(c["type"] for t in tables for c in t["attributes"])

    # --- table-level checks ---
    seen = defaultdict(list)
    for t in tables:
        seen[t["name"].strip().lower()].append(t)

    for name, group in seen.items():
        if len(group) > 1:
            errors.append(_issue(
                "DUPLICATE_TABLE_NAME",
                f"Table name '{group[0]['name']}' is used {len(group)} times.",
                [t["id"] for t in group]))

    for t in tables:
        cols = t["attributes"]
        if not t["name"]:
            errors.append(_issue("UNNAMED_TABLE", "A table has no name.", [t["id"]]))
        if not cols:
            errors.append(_issue(
                "NO_ATTRIBUTES",
                f"Table '{t['name']}' has no columns.", [t["id"]]))
            continue
        if not any(c["is_pk"] for c in cols):
            errors.append(_issue(
                "NO_PRIMARY_KEY",
                f"Table '{t['name']}' has no primary key (PK).",
                [t["id"]]))

        names = defaultdict(list)
        for c in cols:
            names[c["name"].lower()].append(c)
        for cname, group in names.items():
            if len(group) > 1:
                errors.append(_issue(
                    "DUPLICATE_COLUMN",
                    f"Column '{group[0]['name']}' appears {len(group)} times in '{t['name']}'.",
                    [c["id"] for c in group]))
        for c in cols:
            if diagram_has_types and not c["type"]:
                warnings.append(_issue(
                    "MISSING_DATA_TYPE",
                    f"Column '{c['name']}' in '{t['name']}' has no data type.",
                    [c["id"]]))

    # Chen-style (conceptual) diagrams have no foreign-key columns, so FK checks do not apply
    check_fk = model.get("notation") != "chen"

    # --- foreign keys ---
    fk_targets = defaultdict(set)  # table id -> set of table ids it references
    for t in tables:
        for c in t["attributes"]:
            if not c["is_fk"] or not check_fk:
                continue
            target = _resolve_fk(c, t, tables)
            if target is None:
                errors.append(_issue(
                    "INVALID_FOREIGN_KEY",
                    f"Foreign key '{c['name']}' in '{t['name']}' does not reference any existing table.",
                    [t["id"], c["id"]]))
                continue
            fk_targets[t["id"]].add(target["id"])

    # --- relationship checks ---
    connected = set()
    for r in rels:
        label = r["name"] or "unnamed"
        if not r["from"] or not r["to"]:
            errors.append(_issue(
                "DANGLING_RELATIONSHIP",
                f"Relationship '{label}' is not connected to a table at both ends.",
                [r["id"], r["from"], r["to"]]))
            continue

        connected.update([r["from"], r["to"]])
        a, b = by_id[r["from"]], by_id[r["to"]]

        if r["from_column"] or r["to_column"]:
            errors.append(_issue(
                "CONNECTED_TO_COLUMN",
                f"A relationship links '{a['name']}' to '{b['name']}' through a single column. "
                f"Relationships should connect whole tables.",
                [r["id"], r["from_column"], r["to_column"], a["id"], b["id"]]))

        if r["from_cardinality"] is None or r["to_cardinality"] is None:
            warnings.append(_issue(
                "MISSING_CARDINALITY",
                f"Relationship between '{a['name']}' and '{b['name']}' is missing "
                f"a cardinality marker on one or both ends.",
                [r["id"], a["id"], b["id"]]))
            continue

        if r["from_many"] and r["to_many"]:
            warnings.append(_issue(
                "MANY_TO_MANY",
                f"'{a['name']}' and '{b['name']}' form a many-to-many relationship. "
                f"Add a junction table between them.",
                [r["id"], a["id"], b["id"]]))
        elif r["from_many"] != r["to_many"]:
            many, one = (a, b) if r["from_many"] else (b, a)
            if check_fk and one["id"] not in fk_targets[many["id"]]:
                warnings.append(_issue(
                    "MISSING_FOREIGN_KEY",
                    f"'{many['name']}' is on the many side of its relationship with "
                    f"'{one['name']}' but has no foreign key referencing it.",
                    [many["id"], one["id"], r["id"]]))
        else:
            if check_fk and (b["id"] not in fk_targets[a["id"]]
                             and a["id"] not in fk_targets[b["id"]]):
                warnings.append(_issue(
                    "MISSING_FOREIGN_KEY",
                    f"One-to-one relationship between '{a['name']}' and '{b['name']}' "
                    f"has no foreign key on either side.",
                    [a["id"], b["id"], r["id"]]))

    # --- FK present but nothing drawn between the tables ---
    linked = {frozenset((r["from"], r["to"])) for r in rels if r["from"] and r["to"]}
    for t in tables:
        for target_id in (fk_targets[t["id"]] if check_fk else []):
            if frozenset((t["id"], target_id)) not in linked:
                warnings.append(_issue(
                    "FK_WITHOUT_RELATIONSHIP",
                    f"'{t['name']}' has a foreign key to '{by_id[target_id]['name']}' "
                    f"but no relationship line connects them.",
                    [t["id"], target_id]))

    # --- isolated tables ---
    for t in tables:
        if t["id"] not in connected and len(tables) > 1:
            warnings.append(_issue(
                "ISOLATED_TABLE",
                f"Table '{t['name']}' is not connected to any other table.",
                [t["id"]]))

    return {
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
