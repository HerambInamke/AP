import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Report({ onRetake }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  const load = () => api("/reports/me").then(setReport).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  async function deleteMyData() {
    if (!window.confirm(`Delete all your answers and your report for ${report.organization}? This cannot be undone.`)) return;
    try {
      await api("/reports/me", { method: "DELETE" });
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!report) return <p>Loading…</p>;
  if (report.answered === 0) {
    return (
      <div className="card">
        <h2>No report yet</h2>
        <p>You have no saved answers for {report.organization}.</p>
        <button onClick={onRetake}>Take the diagnostic</button>
      </div>
    );
  }
  return (
    <div className="card">
      <h2>{report.name}: {report.level}</h2>
      <p>Average score: {report.average_score ?? "–"} / 5</p>
      <h3>Risks</h3>
      {report.risks.length ? (
        <ul>
          {report.risks.map((r) => (
            <li key={r.risk}><b>{r.label}</b><br />What to do: {r.action}</li>
          ))}
        </ul>
      ) : <p>None found.</p>}
      <h3>Next steps</h3>
      <ul>{report.next_steps.map((s) => <li key={s}>{s}</li>)}</ul>
      <p>
        <button onClick={onRetake}>Retake</button>{" "}
        <button className="danger" onClick={deleteMyData}>Delete my data</button>
      </p>
    </div>
  );
}
