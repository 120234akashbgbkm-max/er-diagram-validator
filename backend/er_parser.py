"""
er_parser.py
Parses draw.io (.drawio) ER diagrams drawn in crow's-foot TABLE notation:

  - each table  = a 'swimlane' shape (title = table name)
  - each column = a child cell inside the table, text like "PK  order_id : INT"
  - each relationship = an edge between tables, with ER arrow markers
    (ERmandOne, ERzeroToMany, ...) and an optional label ("places")
"""

import base64
import html
import re
import zlib
from urllib.parse import unquote
from xml.etree import ElementTree as ET

# draw.io arrow name -> (label, is_many)
ARROWS = {
    "ERone": ("1", False),
    "ERmandOne": ("1", False),
    "ERzeroToOne": ("0..1", False),
    "ERmany": ("N", True),
    "ERoneToMany": ("1..N", True),
    "ERzeroToMany": ("0..N", True),
}

KEY_PREFIX = re.compile(r"^((?:PK|FK|UK)(?:\s*[,/]\s*(?:PK|FK|UK))*)\s+", re.I)


# ---------- reading the file ----------

def _inflate(text):
    data = base64.b64decode(text.strip())
    return unquote(zlib.decompress(data, -15).decode("utf-8"))


def _load_graphs(raw_text):
    """Every page of a draw.io file as a list of <mxGraphModel> elements."""
    raw_text = raw_text.strip()
    root = ET.fromstring(raw_text)
    if root.tag == "mxGraphModel":
        return [root]

    graphs = []
    for diagram in root.iter("diagram"):
        inner = diagram.find("mxGraphModel")
        if inner is not None:                         # uncompressed page
            graphs.append(inner)
        elif (diagram.text or "").strip():            # compressed page
            graphs.append(ET.fromstring(_inflate(diagram.text)))
    if not graphs:
        graphs = list(root.iter("mxGraphModel"))
    if not graphs:
        raise ValueError("No diagram found in this file.")
    return graphs


def _style(style_str):
    out = {}
    for part in (style_str or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
        elif part:
            out[part] = True
    return out


def _clean(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _geometry(cell):
    g = cell.find("mxGeometry")
    if g is None:
        return 0.0, 0.0, 0.0, 0.0
    return (float(g.get("x", 0)), float(g.get("y", 0)),
            float(g.get("width", 0)), float(g.get("height", 0)))


# ---------- parsing a column ----------

def _parse_column(cell):
    text = _clean(cell.get("value"))
    style = _style(cell.get("style"))

    keys = []
    m = KEY_PREFIX.match(text)
    if m:
        keys = [k.upper() for k in re.split(r"[\s,/]+", m.group(1)) if k]
        text = text[m.end():]

    if ":" in text:
        name, dtype = [p.strip() for p in text.split(":", 1)]
    else:
        name, dtype = text.strip(), ""

    # underlined text is also a common way to mark a primary key
    try:
        if int(style.get("fontStyle", 0)) & 4 and "PK" not in keys:
            keys.append("PK")
    except (TypeError, ValueError):
        pass

    return {
        "id": cell.get("id"),
        "name": name,
        "type": dtype,
        "is_pk": "PK" in keys,
        "is_fk": "FK" in keys,
        "is_unique": "UK" in keys,
    }


# ---------- main entry point ----------

def parse_drawio(file_bytes):
    """Parse a draw.io file. If it has several pages, the page with the most tables wins."""
    graphs = _load_graphs(file_bytes.decode("utf-8", errors="replace"))
    best, last_error = None, None
    for g in graphs:
        try:
            model = _parse_graph(g)
        except ValueError as e:
            last_error = e
            continue
        if best is None or len(model["entities"]) > len(best["entities"]):
            best = model
    if best is None:
        raise last_error or ValueError("No tables found.")
    return best


def _parse_graph(graph):
    cells = {c.get("id"): c for c in graph.iter("mxCell")}

    children = {}
    for cid, c in cells.items():
        children.setdefault(c.get("parent"), []).append(c)

    # tables: swimlane shapes, or any shape that has column cells inside it
    tables = {}
    column_to_table = {}
    for cid, c in cells.items():
        if c.get("vertex") != "1":
            continue
        style = _style(c.get("style"))
        kids = [k for k in children.get(cid, []) if k.get("vertex") == "1"]
        if not (("swimlane" in style) or kids):
            continue

        x, y, w, h = _geometry(c)
        columns = [_parse_column(k) for k in kids if _clean(k.get("value"))]
        for col in columns:
            column_to_table[col["id"]] = cid
        tables[cid] = {
            "id": cid,
            "name": _clean(c.get("value")),
            "x": x, "y": y, "width": w, "height": h,
            "attributes": columns,
        }

    if not tables:
        raise ValueError(
            "No tables found. This parser expects crow's-foot style tables "
            "(a swimlane box per table with one row per column)."
        )

    # relationships: edges between tables (or table columns)
    relationships = []
    for cid, c in cells.items():
        if c.get("edge") != "1":
            continue
        style = _style(c.get("style"))

        def resolve(end_id):
            if end_id in tables:
                return end_id, None
            if end_id in column_to_table:
                return column_to_table[end_id], end_id
            return None, None

        src, src_col = resolve(c.get("source"))
        tgt, tgt_col = resolve(c.get("target"))

        start = ARROWS.get(style.get("startArrow"))
        end = ARROWS.get(style.get("endArrow"))

        relationships.append({
            "id": cid,
            "name": _clean(c.get("value")),
            "from": src,
            "to": tgt,
            "from_column": src_col,
            "to_column": tgt_col,
            "from_cardinality": start[0] if start else None,
            "to_cardinality": end[0] if end else None,
            "from_many": bool(start and start[1]),
            "to_many": bool(end and end[1]),
        })

    return {"entities": list(tables.values()), "relationships": relationships, "notation": "crowsfoot"}


def drawio_xml_text(file_bytes):
    """The plain mxGraph XML of every page of a draw.io file (decompressed if needed). Used to let
    the AI read diagrams that are not drawn with table shapes, for example Chen notation."""
    graphs = _load_graphs(file_bytes.decode("utf-8", errors="replace"))
    return "\n".join(ET.tostring(g, encoding="unicode") for g in graphs)
