import { useState } from "react";
import { API } from "../config";
import { downloadReport } from "../utils/report";

const MAX_MB = 15;
const EXACT_TYPES = ["", ".drawio", ".xml", ".sql"]; // read without AI; everything else is read by AI
const extOf = (name = "") => (name.includes(".") ? name.slice(name.lastIndexOf(".")).toLowerCase() : "");

export default function Home() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiIssues, setAiIssues] = useState(null);
  const [downloading, setDownloading] = useState(null);

  const handleFileChange = (event) => {
    const selected = event.target.files[0];
    if (!selected) {
      setFile(null);
    } else if (selected.size > MAX_MB * 1024 * 1024) {
      alert(`This file is larger than ${MAX_MB} MB. Please upload a smaller file.`);
      setFile(null);
    } else {
      setFile(selected);
      setResult(null);
      setAiIssues(null);
    }
  };

  const validateDiagram = async () => {
    if (!file) {
      alert("Please choose a file first");
      return;
    }
    setLoading(true);
    setResult(null);
    setAiIssues(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API}/upload`, { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Validation failed");
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    }
    setLoading(false);
  };

  const runAiReview = async () => {
    if (!result || result.error) return;
    setAiLoading(true);
    setAiIssues(null);

    const { validation, message, notice, source, file_type, ...diagram } = result;
    try {
      const response = await fetch(`${API}/api/ai-review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ diagram, rule_results: validation }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "AI review failed");
      setAiIssues(data.issues);
    } catch (error) {
      setAiIssues({ error: error.message });
    }
    setAiLoading(false);
  };

  const download = async (format) => {
    setDownloading(format);
    try {
      await downloadReport(format, { fileName: file?.name, result, aiIssues });
    } catch (e) {
      alert("Could not create the report: " + e.message);
    }
    setDownloading(null);
  };

  return (
    <div className="page">
      <h1 className="page-title">AI-Based ER Diagram Validator</h1>
      <p className="subtitle">
        Upload your ER diagram and automatically detect structural and design problems.
      </p>

      <div className="card upload-box">
        <h2>Upload ER Diagram</h2>
        <p>
          Any file containing an ER diagram works: <strong>draw.io</strong>, <strong>PDF</strong>,{" "}
          <strong>Word (.docx)</strong>, <strong>images</strong> (PNG, JPG, ...), and{" "}
          <strong>text / SQL / JSON / XML</strong> files.
        </p>
        <input className="file-input" type="file" onChange={handleFileChange} />
        {file && (
          <p className="file-name">
            Selected: <strong>{file.name}</strong>
          </p>
        )}
        <button className="btn btn-primary" onClick={validateDiagram} disabled={loading}>
          {loading
            ? !EXACT_TYPES.includes(extOf(file?.name))
              ? "Reading the diagram with AI (10-30 s)..."
              : "Analyzing..."
            : "Validate Diagram"}
        </button>
      </div>

      {result && result.error && <div className="card result"><p className="text-error">{result.error}</p></div>}

      {result && !result.error && (
        <div className="card result">
          <h2>Validation Result</h2>
          <p className="text-ok strong">{result.message}</p>
          {result.notice && <p className="notice">⚠️ {result.notice}</p>}

          <div className="summary-grid">
            <Stat value={result.validation.error_count} label="Errors" tone="error" />
            <Stat value={result.validation.warning_count} label="Warnings" tone="warn" />
            <Stat value={result.entities.length} label="Tables" />
            <Stat value={result.relationships.length} label="Relationships" />
          </div>

          <IssueList title="Errors" tone="error" icon="❌" items={result.validation.errors} />
          <IssueList title="Warnings" tone="warn" icon="⚠️" items={result.validation.warnings} />

          {result.validation.error_count === 0 && result.validation.warning_count === 0 && (
            <p className="text-ok strong">✓ No problems detected</p>
          )}

          <TableSummary result={result} />

          <div className="action-row">
            <button className="btn btn-primary" onClick={runAiReview} disabled={aiLoading}>
              {aiLoading ? "AI is reviewing..." : "Run AI Review"}
            </button>
          </div>

          {aiIssues && aiIssues.error && <p className="text-error">{aiIssues.error}</p>}

          {Array.isArray(aiIssues) && (
            <div>
              <h3>AI Review</h3>
              {aiIssues.length === 0 && <p className="text-ok strong">✓ AI found no additional problems</p>}
              {aiIssues.map((issue, i) => (
                <div className="issue" key={i}>
                  {issue.severity === "error" ? "❌" : "⚠️"} {issue.message}
                  {issue.suggestion && <div className="issue-tip">💡 {issue.suggestion}</div>}
                </div>
              ))}
            </div>
          )}

          <div className="download-box">
            <h3>Download Report</h3>
            <p className="muted">
              Includes your input, the processing steps, the parsed tables, and the final results
              {Array.isArray(aiIssues) ? " (with the AI review)." : ". Run the AI review first to include it."}
            </p>
            <div className="action-row">
              <button className="btn btn-outline" onClick={() => download("pdf")} disabled={!!downloading}>
                {downloading === "pdf" ? "Preparing..." : "⬇ PDF"}
              </button>
              <button className="btn btn-outline" onClick={() => download("doc")} disabled={!!downloading}>
                ⬇ Word Document
              </button>
              <button className="btn btn-outline" onClick={() => download("txt")} disabled={!!downloading}>
                ⬇ Text
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ value, label, tone }) {
  return (
    <div className="stat">
      <span className={`stat-number ${tone ? `text-${tone}` : ""}`}>{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function IssueList({ title, tone, icon, items }) {
  if (!items.length) return null;
  return (
    <div>
      <h3 className={`text-${tone}`}>{title}</h3>
      {items.map((it, i) => (
        <div className="issue" key={i}>
          {icon} {it.message}
        </div>
      ))}
    </div>
  );
}

function TableSummary({ result }) {
  const { entities, relationships, validation } = result;
  const errorIds = new Set(validation.errors.flatMap((e) => e.element_ids));
  const warnIds = new Set(validation.warnings.flatMap((w) => w.element_ids));
  const relCount = (id) => relationships.filter((r) => r.from === id || r.to === id).length;

  return (
    <div className="table-summary">
      <h3>Table Summary</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Table</th>
              <th>Columns</th>
              <th>Primary key</th>
              <th>Foreign keys</th>
              <th>Relationships</th>
            </tr>
          </thead>
          <tbody>
            {entities.map((e) => {
              const pks = e.attributes.filter((a) => a.is_pk).map((a) => a.name);
              const fks = e.attributes.filter((a) => a.is_fk).map((a) => a.name);
              const cls = errorIds.has(e.id) ? "row-error" : warnIds.has(e.id) ? "row-warn" : "";
              return (
                <tr key={e.id} className={cls}>
                  <td className="strong">{e.name || "(unnamed)"}</td>
                  <td>{e.attributes.length}</td>
                  <td>{pks.length ? pks.join(", ") : "—"}</td>
                  <td>{fks.length ? fks.join(", ") : "—"}</td>
                  <td>{relCount(e.id)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="muted small">Rows in red have an error; rows in amber have a warning.</p>

      <div className="table-cards">
        {entities.map((e) => (
          <div className="mini-table" key={e.id}>
            <div className="mini-table-title">{e.name || "(unnamed)"}</div>
            {e.attributes.length === 0 && <div className="mini-col muted">no columns</div>}
            {e.attributes.map((a) => (
              <div className="mini-col" key={a.id}>
                <span>
                  {a.is_pk && <b className="badge badge-pk">PK</b>}
                  {a.is_fk && <b className="badge badge-fk">FK</b>}
                  {a.name}
                </span>
                <span className="muted">{a.type}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
