import { useState } from "react";

// ---- Edit these details if anything is wrong ----
const PROJECT = "AI-Based ER Diagram Validator";
const TEAM_NO = 2;
const TEAM = [
  // Put each member's photo in frontend/public/ and set the file name here.
  { name: "Akash B", reg: "25BCE5756", photo: "/student.jpg" },
];
const GUIDE = { name: "Dr. Swaminathan A", role: "Assistant Professor", photo: "/faculty.png" };
// -------------------------------------------------

function Photo({ src, name }) {
  const [failed, setFailed] = useState(false);
  const initials = name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  if (failed) return <div className="photo photo-fallback">{initials}</div>;
  return <img className="photo" src={src} alt={name} onError={() => setFailed(true)} />;
}

export default function DevelopedBy() {
  return (
    <div className="page">
      <h1 className="page-title">Developed By</h1>
      <p className="subtitle">
        {PROJECT} · Team {TEAM_NO}
      </p>

      <h2 className="section-title">Team</h2>
      <div className="people">
        {TEAM.map((m) => (
          <div className="card person" key={m.reg}>
            <Photo src={m.photo} name={m.name} />
            <div className="person-name">{m.name}</div>
            <div className="muted">Register No: {m.reg}</div>
          </div>
        ))}
      </div>

      <h2 className="section-title">Guided By</h2>
      <div className="people">
        <div className="card person">
          <Photo src={GUIDE.photo} name={GUIDE.name} />
          <div className="person-name">{GUIDE.name}</div>
          <div className="muted">{GUIDE.role}</div>
        </div>
      </div>

      <p className="center muted">
        Done under faculty <b>{GUIDE.name}</b>
      </p>
    </div>
  );
}
