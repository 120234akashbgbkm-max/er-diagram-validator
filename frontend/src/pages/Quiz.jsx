import { useState } from "react";
import { API } from "../config";

const LETTERS = ["A", "B", "C", "D"];

export default function Quiz() {
  const [stage, setStage] = useState("setup"); // setup | loading | question | summary
  const [count, setCount] = useState(5);
  const [difficulty, setDifficulty] = useState("Easy");
  const [questions, setQuestions] = useState([]);
  const [source, setSource] = useState("ai");
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState([]); // { picked, correct }
  const [error, setError] = useState(null);

  const start = async () => {
    setError(null);
    setStage("loading");
    try {
      const res = await fetch(`${API}/api/quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count, difficulty }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Could not create the quiz.");
      if (!data.questions.length) throw new Error("No questions were returned.");
      setQuestions(data.questions);
      setSource(data.source);
      setIdx(0);
      setSelected(null);
      setSubmitted(false);
      setResults([]);
      setStage("question");
    } catch (e) {
      setError(e.message);
      setStage("setup");
    }
  };

  const q = questions[idx];

  const submit = () => {
    if (selected === null) return;
    setSubmitted(true);
    setResults((r) => [...r, { picked: selected, correct: selected === q.correct_index }]);
  };

  const next = () => {
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
      setSelected(null);
      setSubmitted(false);
    } else {
      setStage("summary");
    }
  };

  const score = results.filter((r) => r.correct).length;

  if (stage === "setup" || stage === "loading") {
    return (
      <div className="page narrow">
        <h1 className="page-title">QUIZ</h1>
        <p className="subtitle">Test yourself on ER diagrams and database design.</p>

        <div className="card">
          <label className="field">
            <span>Number of questions (1 – 20)</span>
            <input
              type="number"
              min="1"
              max="20"
              value={count}
              onChange={(e) => setCount(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}
            />
          </label>

          <div className="field">
            <span>Difficulty level</span>
            <div className="chip-row">
              {["Easy", "Medium", "Hard"].map((d) => (
                <button
                  key={d}
                  className={`chip ${difficulty === d ? "chip-active" : ""}`}
                  onClick={() => setDifficulty(d)}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-error">{error}</p>}

          <button className="btn btn-primary" onClick={start} disabled={stage === "loading"}>
            {stage === "loading" ? "AI is writing your questions..." : "Start Quiz"}
          </button>
        </div>
      </div>
    );
  }

  if (stage === "summary") {
    const pct = Math.round((score / questions.length) * 100);
    return (
      <div className="page narrow">
        <h1 className="page-title">Quiz Complete</h1>
        <div className="card center">
          <div className="big-score">
            {score} / {questions.length}
          </div>
          <p className="muted">
            {pct}% correct · {difficulty} level
          </p>
          <p className="strong">
            {pct >= 80 ? "Excellent work!" : pct >= 50 ? "Good effort. Review the ones you missed." : "Keep practising. Check the Learn page and try again."}
          </p>
        </div>

        <div className="card">
          <h3>Your performance</h3>
          {questions.map((qq, i) => (
            <div key={i} className={`review-row ${results[i]?.correct ? "ok" : "bad"}`}>
              <div className="strong">
                {results[i]?.correct ? "✓" : "✗"} Q{i + 1}. {qq.question}
              </div>
              <div className="small">
                Your answer: {LETTERS[results[i]?.picked]}. {qq.options[results[i]?.picked]}
              </div>
              {!results[i]?.correct && (
                <div className="small">
                  Correct answer: {LETTERS[qq.correct_index]}. {qq.options[qq.correct_index]}
                </div>
              )}
            </div>
          ))}
        </div>

        <button className="btn btn-primary" onClick={() => setStage("setup")}>
          Take another quiz
        </button>
      </div>
    );
  }

  const isCorrect = submitted && selected === q.correct_index;

  return (
    <div className="page narrow">
      <div className="quiz-top">
        <span className="muted">
          Question {idx + 1} of {questions.length} · {difficulty}
        </span>
        <span className="muted">Score: {score}</span>
      </div>
      <div className="progress">
        <div className="progress-bar" style={{ width: `${((idx + (submitted ? 1 : 0)) / questions.length) * 100}%` }} />
      </div>

      {source === "bank" && (
        <p className="notice">The AI was unavailable, so these questions come from the built-in question bank.</p>
      )}

      <div className="card">
        <h2 className="question-text">{q.question}</h2>

        <div className="options">
          {q.options.map((opt, i) => {
            let cls = "option";
            if (submitted) {
              if (i === q.correct_index) cls += " option-correct";
              else if (i === selected) cls += " option-wrong";
            } else if (i === selected) cls += " option-selected";
            return (
              <button key={i} className={cls} disabled={submitted} onClick={() => setSelected(i)}>
                <span className="option-letter">{LETTERS[i]}</span>
                {opt}
              </button>
            );
          })}
        </div>

        {!submitted && (
          <button className="btn btn-primary" onClick={submit} disabled={selected === null}>
            Submit Answer
          </button>
        )}

        {submitted && (
          <div className={`feedback ${isCorrect ? "feedback-ok" : "feedback-bad"}`}>
            <div className="strong">
              {isCorrect ? "Yes, you have correctly answered the question." : "Yet to answer correctly."}
            </div>
            <p>
              <b>Correct answer:</b> {LETTERS[q.correct_index]}. {q.options[q.correct_index]}
            </p>
            <p className="pre">
              <b>Explanation:</b> {q.explanation}
            </p>
            <button className="btn btn-primary" onClick={next}>
              {idx + 1 < questions.length ? "Next Question" : "See Results"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
