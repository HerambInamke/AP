import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Diagnostic({ onDone }) {
  const [questions, setQuestions] = useState(null);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api("/diagnostic/questions").then(setQuestions).catch((e) => setError(e.message));
  }, []);

  const set = (id, value) => setAnswers({ ...answers, [id]: value });
  const unanswered = (questions || []).filter((q) => !(answers[q.id] || "").trim()).length;

  async function submit() {
    if (unanswered) return setError(`Please answer all questions (${unanswered} left).`);
    setSubmitting(true);
    setError("");
    try {
      const payload = questions.map((q) => ({ question_id: q.id, answer: answers[q.id] }));
      await api("/diagnostic/submit", { method: "POST", body: JSON.stringify({ answers: payload }) });
      onDone();
    } catch (e) {
      setError(e.message);
      setSubmitting(false);
    }
  }

  if (!questions) return error ? <p className="error">{error}</p> : <p>Loading…</p>;
  return (
    <div className="card">
      <h2>Your AI diagnostic</h2>
      {questions.map((q) => (
        <div key={q.id}>
          <label htmlFor={q.id}><b>{q.text}</b></label>
          {q.type === "mcq" ? (
            <select id={q.id} onChange={(e) => set(q.id, e.target.value)} defaultValue="">
              <option value="" disabled>Choose…</option>
              {q.options.map((o) => <option key={o}>{o}</option>)}
            </select>
          ) : (
            <textarea id={q.id} rows={4} maxLength={2000} onChange={(e) => set(q.id, e.target.value)} />
          )}
        </div>
      ))}
      {error && <p className="error">{error}</p>}
      <button onClick={submit} disabled={submitting}>{submitting ? "Scoring…" : "Submit"}</button>
    </div>
  );
}
