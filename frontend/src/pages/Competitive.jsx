import { useEffect, useState } from "react";
import { API } from "../config";

const LETTERS = ["A", "B", "C", "D"];

export default function Competitive() {
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");
  const [open, setOpen] = useState({}); // id -> bool

  useEffect(() => {
    fetch(`${API}/api/competitive`)
      .then((r) => r.json())
      .then((d) => setQuestions(d.questions || []))
      .catch(() => setError("Could not load the questions. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  const shown = questions.filter((q) => filter === "All" || q.difficulty === filter);
  const allOpen = shown.length > 0 && shown.every((q) => open[q.id]);
  const toggleAll = () => {
    const next = { ...open };
    shown.forEach((q) => (next[q.id] = !allOpen));
    setOpen(next);
  };

  return (
    <div className="page">
      <h1 className="page-title">COMPETITIVE EXAM</h1>
      <p className="subtitle">
        {questions.length} solved practice questions on ER modelling, keys and normalization for GATE / PSU style exams.
      </p>

      <p className="notice">
        These are original practice questions written in the style of GATE and PSU database papers, not copies of past
        papers, so they are tagged as practice and carry no exam year.
      </p>

      <div className="toolbar">
        <div className="chip-row">
          {["All", "Easy", "Medium", "Hard"].map((f) => (
            <button key={f} className={`chip ${filter === f ? "chip-active" : ""}`} onClick={() => setFilter(f)}>
              {f}
            </button>
          ))}
        </div>
        <button className="btn btn-outline" onClick={toggleAll}>
          {allOpen ? "Hide all solutions" : "Show all solutions"}
        </button>
      </div>

      {loading && <p className="muted">Loading questions...</p>}
      {error && <p className="text-error">{error}</p>}

      {shown.map((q, n) => (
        <div className="card exam-card" key={q.id}>
          <div className="exam-meta">
            <span className="muted">Question {q.id}</span>
            <span>
              <span className={`tag tag-${q.difficulty.toLowerCase()}`}>{q.difficulty}</span>
              <span className="tag">{q.topic}</span>
            </span>
          </div>

          <p className="question-text">{q.question}</p>

          <ol className="exam-options" type="A">
            {q.options.map((o, i) => (
              <li key={i} className={open[q.id] && i === q.answer ? "option-correct-text" : ""}>
                {o}
              </li>
            ))}
          </ol>

          <button className="btn btn-outline small-btn" onClick={() => setOpen({ ...open, [q.id]: !open[q.id] })}>
            {open[q.id] ? "Hide solution" : "Show solution"}
          </button>

          {open[q.id] && (
            <div className="solution">
              <p>
                <b>Correct answer:</b> {LETTERS[q.answer]}. {q.options[q.answer]}
              </p>
              <p className="pre">
                <b>Solution:</b> {q.explanation}
              </p>
              <p className="muted small">
                <b>Tag:</b> {q.tag}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
