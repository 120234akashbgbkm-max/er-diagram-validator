"""
sql_parser.py
Reads CREATE TABLE (and ALTER TABLE ... ADD FOREIGN KEY / PRIMARY KEY) statements and
returns the "extracted" format used by er_model.build_model. No AI involved: the result is exact.
"""

import re

_COL_STOP = r"(?:NOT|NULL|DEFAULT|PRIMARY|REFERENCES|UNIQUE|CHECK|AUTO_INCREMENT|AUTOINCREMENT|IDENTITY|COLLATE|GENERATED|CONSTRAINT|COMMENT|ON)"


def _strip_comments(sql):
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def _ident(token):
    token = token.strip().strip(",")
    token = token.split(".")[-1]
    return token.strip('`"[]').strip()


def _ident_list(text):
    return [_ident(x) for x in text.split(",") if x.strip()]


def _balanced(text, open_pos):
    """Return (inside, end_index) for the parenthesis starting at open_pos."""
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[open_pos + 1:i], i
    return text[open_pos + 1:], len(text)


def _split_top(body):
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


_REF = re.compile(r"REFERENCES\s+([^\s(]+)\s*(?:\(([^)]*)\))?", re.I)


def parse_sql(text):
    text = _strip_comments(text)
    tables = {}  # lower name -> dict
    order = []
    fks = []  # (child, [cols], parent)

    create = re.compile(
        r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:GLOBAL\s+|LOCAL\s+)?TEMP(?:ORARY)?\s+)?TABLE\s+"
        r"(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)\s*\(", re.I)

    for m in create.finditer(text):
        name = _ident(m.group(1))
        body, _ = _balanced(text, m.end() - 1)
        t = {"name": name, "columns": [], "pk": [], "unique": set()}

        for part in _split_top(body):
            if not part:
                continue
            up = part.upper().lstrip()
            core = re.sub(r"^CONSTRAINT\s+\S+\s+", "", part.strip(), flags=re.I)
            core_up = core.upper()

            if core_up.startswith("PRIMARY KEY"):
                inner = re.search(r"\((.*)\)", core, re.S)
                if inner:
                    t["pk"] += _ident_list(inner.group(1))
            elif core_up.startswith("FOREIGN KEY"):
                inner = re.search(r"FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s+([^\s(]+)", core, re.I | re.S)
                if inner:
                    fks.append((name, _ident_list(inner.group(1)), _ident(inner.group(2))))
            elif core_up.startswith("UNIQUE"):
                inner = re.search(r"\((.*)\)", core, re.S)
                if inner:
                    cols = _ident_list(inner.group(1))
                    if len(cols) == 1:
                        t["unique"].add(cols[0].lower())
            elif re.match(r"(KEY|INDEX|CHECK|FULLTEXT|SPATIAL|EXCLUDE)\b", up):
                continue
            else:
                cm = re.match(r'\s*([`"\[]?[\w$ ]+?[`"\]]?)\s+(.*)$', part.strip(), re.S)
                if not cm:
                    continue
                cname = _ident(cm.group(1))
                rest = cm.group(2)
                tm = re.match(
                    rf"([A-Za-z_][\w ]*?(?:\s*\([^)]*\))?)\s*(?=\b{_COL_STOP}\b|$)", rest, re.I | re.S)
                ctype = re.sub(r"\s+", " ", tm.group(1)).strip() if tm else rest.split()[0]
                rest_up = rest.upper()
                col = {"name": cname, "type": ctype, "keys": [],
                       "not_null": "NOT NULL" in rest_up}
                if "PRIMARY KEY" in rest_up:
                    t["pk"].append(cname)
                if re.search(r"\bUNIQUE\b", rest_up):
                    t["unique"].add(cname.lower())
                rm = _REF.search(rest)
                if rm:
                    fks.append((name, [cname], _ident(rm.group(1))))
                t["columns"].append(col)

        tables[name.lower()] = t
        order.append(name.lower())

    # ALTER TABLE ... ADD [CONSTRAINT x] FOREIGN KEY (...) REFERENCES p / ADD PRIMARY KEY (...)
    for am in re.finditer(r"ALTER\s+TABLE\s+(?:ONLY\s+)?(?:IF\s+EXISTS\s+)?([^\s]+)\s+(.*?);", text, re.I | re.S):
        tname = _ident(am.group(1))
        clause = am.group(2)
        fm = re.search(r"FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s+([^\s(]+)", clause, re.I | re.S)
        if fm:
            fks.append((tname, _ident_list(fm.group(1)), _ident(fm.group(2))))
        pm = re.search(r"PRIMARY\s+KEY\s*\((.*?)\)", clause, re.I | re.S)
        if pm and tname.lower() in tables:
            tables[tname.lower()]["pk"] += _ident_list(pm.group(1))

    if not order:
        raise ValueError("No CREATE TABLE statements were found in the SQL file.")

    # apply primary keys and foreign keys to the columns
    for key in order:
        t = tables[key]
        pk = {c.lower() for c in t["pk"]}
        for col in t["columns"]:
            if col["name"].lower() in pk:
                col["keys"].append("PK")
            if col["name"].lower() in t["unique"]:
                col["keys"].append("UK")

    relationships = []
    for child, cols, parent in fks:
        ct = tables.get(child.lower())
        if not ct:
            continue
        for col in ct["columns"]:
            if col["name"].lower() in {c.lower() for c in cols}:
                if "FK" not in col["keys"]:
                    col["keys"].append("FK")
                col["references"] = parent
        if parent.lower() not in tables:
            continue  # the validator will flag this FK as pointing at a missing table
        pk = {c.lower() for c in ct["pk"]}
        fk_set = {c.lower() for c in cols}
        single_unique = len(cols) == 1 and cols[0].lower() in ct["unique"]
        child_one = fk_set == pk or single_unique
        all_not_null = all(
            next((c for c in ct["columns"] if c["name"].lower() == x), {}).get("not_null", False)
            or x in pk for x in fk_set)
        relationships.append({
            "name": "references",
            "from": tables[parent.lower()]["name"],
            "to": ct["name"],
            "from_cardinality": "1" if all_not_null else "0..1",
            "to_cardinality": "1" if child_one else "0..N",
        })

    for t in tables.values():
        for col in t["columns"]:
            col.pop("not_null", None)

    return {
        "notation": "sql",
        "tables": [{"name": tables[k]["name"], "columns": tables[k]["columns"]} for k in order],
        "relationships": relationships,
    }
