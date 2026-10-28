import { useEffect, useState } from "react";
import "./App.css";
import Home from "./pages/Home.jsx";
import Quiz from "./pages/Quiz.jsx";
import Competitive from "./pages/Competitive.jsx";
import Help from "./pages/Help.jsx";
import DevelopedBy from "./pages/DevelopedBy.jsx";
import Learn from "./pages/Learn.jsx";

const NAV = [
  { id: "home", label: "Home" },
  { id: "quiz", label: "QUIZ" },
  { id: "exam", label: "COMPETITIVE EXAM" },
  { id: "help", label: "Help" },
  { id: "developed", label: "Developed By" },
  { id: "learn", label: "Learn" }, // Learn sits at the top-right, as the rubric asks
];

function getInitialTheme() {
  try {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    /* ignore */
  }
  return "dark";
}

export default function App() {
  const [page, setPage] = useState("home");
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("theme", theme);
    } catch {
      /* ignore */
    }
  }, [theme]);

  const go = (id) => {
    setPage(id);
    window.scrollTo({ top: 0 });
  };

  return (
    <div className="app">
      <header className="navbar">
        <button className="brand" onClick={() => go("home")}>
          <span className="brand-mark">⌸</span> ER Validator
        </button>

        <nav className="nav-links">
          {NAV.map((n) => (
            <button
              key={n.id}
              className={`nav-btn ${page === n.id ? "nav-active" : ""}`}
              onClick={() => go(n.id)}
            >
              {n.label}
            </button>
          ))}
          <button
            className="theme-toggle"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            title={theme === "dark" ? "Switch to Day mode" : "Switch to Night mode"}
          >
            {theme === "dark" ? "☀️ Day" : "🌙 Night"}
          </button>
        </nav>
      </header>

      {/* Home stays mounted so your uploaded file and results survive switching tabs */}
      <div hidden={page !== "home"}>
        <Home />
      </div>
      {page === "quiz" && <Quiz />}
      {page === "exam" && <Competitive />}
      {page === "help" && <Help />}
      {page === "developed" && <DevelopedBy />}
      {page === "learn" && <Learn />}
    </div>
  );
}
