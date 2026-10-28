import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const fmt = (v) => (v === null || v === undefined ? "–" : v);

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/dashboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading…</p>;
  const other = data.other_teams;

  return (
    <>
      <div className="card">
        <h2>{data.organization}</h2>
        <p>
          {data.respondents} people have taken the diagnostic.
          {data.overall && <> Overall level: <b>{data.overall.level}</b> ({data.overall.average_score} / 5).</>}
        </p>
        <table>
          <thead>
            <tr><th>Team</th><th>Responded</th><th>Average</th><th>Level</th></tr>
          </thead>
          <tbody>
            {data.departments.map((d) => (
              <tr key={d.department}>
                <td>{d.department}</td>
                <td>{d.respondents} / {d.employees}</td>
                <td>{fmt(d.average_score)}</td>
                <td>{d.level}</td>
              </tr>
            ))}
            {other && (
              <tr className="muted">
                <td>{other.department}<br /><small>{other.includes.join(", ")}</small></td>
                {other.hidden ? (
                  <td colSpan={3}>Not shown: fewer than {data.min_group_size} responses in total</td>
                ) : (
                  <>
                    <td>{other.respondents}</td>
                    <td>{fmt(other.average_score)}</td>
                    <td>{other.level}</td>
                  </>
                )}
              </tr>
            )}
          </tbody>
        </table>
        <p><small>
          To protect individuals, a team only appears on its own once at least {data.min_group_size} people
          in it have responded. Smaller teams are combined into "Other teams".
        </small></p>
      </div>
      <div className="card">
        <h3>Top risks and what to do</h3>
        {data.top_risks.length === 0 ? (
          <p>No risks to show yet.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Risk</th><th>People</th><th>Where</th><th>Do this</th></tr>
            </thead>
            <tbody>
              {data.top_risks.map((r) => (
                <tr key={r.risk}>
                  <td>{r.label}</td>
                  <td>{r.people} <small>({Math.round(r.share * 100)}%)</small></td>
                  <td>{r.teams.map((t) => <div key={t.team}>{t.team}: {t.people} of {t.of}</div>)}</td>
                  <td>{r.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
