// Builds the downloadable report (TXT / Word / PDF) from the validation result.

const latin1 = (s) => String(s ?? "").replace(/[^\x00-\xFF]/g, "-");
const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const SOURCES = {
  drawio: ["draw.io diagram (.drawio)", "The XML was parsed: tables, columns (with PK/FK markers) and relationship lines were extracted."],
  sql: ["SQL script (.sql)", "The CREATE TABLE statements were parsed exactly: tables, columns, primary keys and foreign keys were extracted."],
  "ai-image": ["Image of an ER diagram", "The AI (Gemini) read the image and extracted tables, columns and relationships. This extraction should be checked against the original diagram."],
  "ai-pdf": ["PDF containing an ER diagram", "The AI (Gemini) read the PDF and extracted tables, columns and relationships. This extraction should be checked against the original diagram."],
  "ai-office": ["Word / Office document", "The text and pictures in the document were read by the AI (Gemini), which extracted tables, columns and relationships. This extraction should be checked against the original."],
  "ai-text": ["Text description of an ER diagram", "The AI (Gemini) read the text and extracted tables, columns and relationships. This extraction should be checked against the original."],
  "ai-drawio": ["draw.io diagram (non-table notation)", "The draw.io XML was interpreted by the AI (Gemini), because the diagram does not use table shapes. This extraction should be checked against the original diagram."],
};

export function buildReport({ fileName, result, aiIssues }) {
  const v = result.validation;
  const nameOf = (id) => result.entities.find((e) => e.id === id)?.name || "?";

  const tables = result.entities.map((e) => ({
    name: e.name,
    columns: e.attributes.map((a) => ({
      name: a.name,
      type: a.type || "-",
      key: [a.is_pk && "PK", a.is_fk && "FK", a.is_unique && "UK"].filter(Boolean).join(", ") || "-",
    })),
  }));

  const relationships = result.relationships.map(
    (r) =>
      `${nameOf(r.from)} (${r.from_cardinality || "?"})  --  ${r.name || "unnamed"}  --  (${
        r.to_cardinality || "?"
      }) ${nameOf(r.to)}`
  );

  const ai = Array.isArray(aiIssues) ? aiIssues : null;

  return {
    title: "ER Diagram Validation Report",
    generatedAt: new Date().toLocaleString(),
    inputs: [`Uploaded file: ${fileName || "unknown"}`, `File type: ${(SOURCES[result.source] || SOURCES.drawio)[0]}`],
    steps: [
      "1. The file was uploaded to the backend (FastAPI).",
      `2. ${(SOURCES[result.source] || SOURCES.drawio)[1]}`,
      "3. Rule-based validation checked keys, foreign keys, cardinality, connections and naming.",
      ai
        ? "4. The AI review (Gemini) examined the design for semantic problems such as normalization."
        : "4. The AI review was not run for this report.",
    ],
    tables,
    relationships,
    summary: [
      `Tables parsed: ${result.entities.length}`,
      `Relationships parsed: ${result.relationships.length}`,
      `Errors: ${v.error_count}`,
      `Warnings: ${v.warning_count}`,
      `AI findings: ${ai ? ai.length : "not run"}`,
    ],
    errors: v.errors.map((e) => e.message),
    warnings: v.warnings.map((w) => w.message),
    ai: ai ? ai.map((i) => ({ severity: i.severity, message: i.message, suggestion: i.suggestion || "" })) : null,
  };
}

// ---------- plain text ----------
export function toText(r) {
  const L = [];
  const h = (t) => L.push("", t.toUpperCase(), "-".repeat(t.length));
  L.push(r.title, `Generated: ${r.generatedAt}`);
  h("1. User inputs");
  r.inputs.forEach((x) => L.push(x));
  h("2. Processing steps");
  r.steps.forEach((x) => L.push(x));
  h("3. Intermediate results: parsed tables");
  r.tables.forEach((t) => {
    L.push("", `Table: ${t.name}`);
    t.columns.forEach((c) => L.push(`   ${c.name.padEnd(22)} ${c.type.padEnd(14)} ${c.key}`));
  });
  h("4. Intermediate results: relationships");
  r.relationships.length ? r.relationships.forEach((x) => L.push(x)) : L.push("None found.");
  h("5. Final output");
  r.summary.forEach((x) => L.push(x));
  L.push("", "Errors:");
  r.errors.length ? r.errors.forEach((x) => L.push(`  [ERROR] ${x}`)) : L.push("  None");
  L.push("", "Warnings:");
  r.warnings.length ? r.warnings.forEach((x) => L.push(`  [WARNING] ${x}`)) : L.push("  None");
  L.push("", "AI review:");
  if (!r.ai) L.push("  Not run.");
  else if (!r.ai.length) L.push("  No additional problems found.");
  else
    r.ai.forEach((i) => {
      L.push(`  [${(i.severity || "warning").toUpperCase()}] ${i.message}`);
      if (i.suggestion) L.push(`      Suggestion: ${i.suggestion}`);
    });
  return L.join("\n");
}

// ---------- Word (HTML saved as .doc, opens in Word) ----------
export function toHtml(r) {
  const list = (items, cls = "") =>
    items.length
      ? `<ul>${items.map((x) => `<li${cls ? ` class="${cls}"` : ""}>${esc(x)}</li>`).join("")}</ul>`
      : "<p>None</p>";
  const tableHtml = r.tables
    .map(
      (t) => `<h3>${esc(t.name)}</h3>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;width:100%">
<tr style="background:#dbe4f3"><th align="left">Column</th><th align="left">Type</th><th align="left">Key</th></tr>
${t.columns.map((c) => `<tr><td>${esc(c.name)}</td><td>${esc(c.type)}</td><td>${esc(c.key)}</td></tr>`).join("")}
</table>`
    )
    .join("");
  const aiHtml = !r.ai
    ? "<p>Not run.</p>"
    : !r.ai.length
    ? "<p>No additional problems found.</p>"
    : `<ul>${r.ai
        .map(
          (i) =>
            `<li><b>${esc((i.severity || "warning").toUpperCase())}:</b> ${esc(i.message)}${
              i.suggestion ? `<br><i>Suggestion: ${esc(i.suggestion)}</i>` : ""
            }</li>`
        )
        .join("")}</ul>`;

  return `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
<head><meta charset="utf-8"><title>${esc(r.title)}</title>
<style>body{font-family:Calibri,Arial,sans-serif;font-size:11pt} h1{color:#1e3a8a} h2{color:#1e3a8a;border-bottom:1px solid #999} li.e{color:#b91c1c} li.w{color:#b45309}</style></head>
<body>
<h1>${esc(r.title)}</h1><p>Generated: ${esc(r.generatedAt)}</p>
<h2>1. User inputs</h2>${list(r.inputs)}
<h2>2. Processing steps</h2>${list(r.steps)}
<h2>3. Intermediate results: parsed tables</h2>${tableHtml}
<h2>4. Intermediate results: relationships</h2>${list(r.relationships)}
<h2>5. Final output</h2>${list(r.summary)}
<h3>Errors</h3>${list(r.errors, "e")}
<h3>Warnings</h3>${list(r.warnings, "w")}
<h3>AI review</h3>${aiHtml}
</body></html>`;
}

// ---------- PDF ----------
export async function toPdf(r) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();
  const M = 44;
  let y = M;

  const need = (h) => {
    if (y + h > H - M) {
      doc.addPage();
      y = M;
    }
  };
  const text = (s, { size = 10.5, bold = false, color = [30, 30, 30], indent = 0, gap = 4, mono = false } = {}) => {
    doc.setFont(mono ? "courier" : "helvetica", bold ? "bold" : "normal");
    doc.setFontSize(size);
    doc.setTextColor(...color);
    const lines = doc.splitTextToSize(latin1(s), W - 2 * M - indent);
    lines.forEach((ln) => {
      need(size + 3);
      doc.text(ln, M + indent, y);
      y += size + 3;
    });
    y += gap;
  };
  const heading = (s) => {
    y += 6;
    need(30);
    text(s, { size: 13, bold: true, color: [30, 58, 138], gap: 2 });
    doc.setDrawColor(150);
    doc.line(M, y - 2, W - M, y - 2);
    y += 14;
  };

  text(r.title, { size: 20, bold: true, color: [30, 58, 138], gap: 2 });
  text(`Generated: ${r.generatedAt}`, { size: 9, color: [100, 100, 100], gap: 8 });

  heading("1. User inputs");
  r.inputs.forEach((x) => text(x, { indent: 8, gap: 1 }));
  heading("2. Processing steps");
  r.steps.forEach((x) => text(x, { indent: 8, gap: 1 }));
  heading("3. Intermediate results: parsed tables");
  r.tables.forEach((t) => {
    text(`Table: ${t.name}`, { bold: true, gap: 1, indent: 4 });
    t.columns.forEach((c) =>
      text(`${c.name.padEnd(22)} ${c.type.padEnd(14)} ${c.key}`, { size: 9, mono: true, indent: 16, gap: 0 })
    );
    y += 6;
  });
  heading("4. Intermediate results: relationships");
  r.relationships.length
    ? r.relationships.forEach((x) => text(x, { indent: 8, gap: 1 }))
    : text("None found.", { indent: 8 });
  heading("5. Final output");
  r.summary.forEach((x) => text(x, { indent: 8, gap: 1 }));
  text("Errors", { bold: true, color: [185, 28, 28], gap: 1 });
  r.errors.length
    ? r.errors.forEach((x) => text(`- ${x}`, { indent: 8, gap: 1 }))
    : text("None", { indent: 8 });
  text("Warnings", { bold: true, color: [180, 83, 9], gap: 1 });
  r.warnings.length
    ? r.warnings.forEach((x) => text(`- ${x}`, { indent: 8, gap: 1 }))
    : text("None", { indent: 8 });
  text("AI review", { bold: true, gap: 1 });
  if (!r.ai) text("Not run.", { indent: 8 });
  else if (!r.ai.length) text("No additional problems found.", { indent: 8 });
  else
    r.ai.forEach((i) => {
      text(`[${(i.severity || "warning").toUpperCase()}] ${i.message}`, { indent: 8, gap: 1 });
      if (i.suggestion) text(`Suggestion: ${i.suggestion}`, { indent: 20, gap: 3, color: [90, 90, 90] });
    });

  return doc.output("blob");
}

// ---------- trigger a browser download ----------
function save(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function downloadReport(format, data) {
  const report = buildReport(data);
  const base = "ER_Validation_Report";
  if (format === "txt") save(new Blob([toText(report)], { type: "text/plain" }), `${base}.txt`);
  else if (format === "doc")
    save(new Blob(["\ufeff", toHtml(report)], { type: "application/msword" }), `${base}.doc`);
  else save(await toPdf(report), `${base}.pdf`);
}
