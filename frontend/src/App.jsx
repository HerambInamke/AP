import React, { useEffect, useState } from "react";
import { api, setToken } from "./api.js";
import Login from "./pages/Login.jsx";
import OrgPicker from "./pages/OrgPicker.jsx";
import Diagnostic from "./pages/Diagnostic.jsx";
import Report from "./pages/Report.jsx";
import Dashboard from "./pages/Dashboard.jsx";

export default function App() {
  const [step, setStep] = useState("login");
  const [session, setSession] = useState(null);
  const [org, setOrg] = useState(null);

  function logout() {
    setToken(null);
    setSession(null);
    setOrg(null);
    setStep("login");
  }

  useEffect(() => {
    window.addEventListener("auth-expired", logout);
    return () => window.removeEventListener("auth-expired", logout);
  }, []);

  async function pickOrg(o) {
    setOrg(o);
    if (o.role === "admin") return setStep("dashboard");
    // Employees who already took the diagnostic land on their report, not a retake
    const report = await api("/reports/me").catch(() => null);
    setStep(report && report.answered > 0 ? "report" : "diagnostic");
  }

  return (
    <div className="wrap">
      <header className="top">
        <h1>AI Pulse</h1>
        {session && (
          <span>
            {session.name}{org ? ` · ${org.org_name}` : ""}{" "}
            {session.organizations.length > 1 && org && (
              <button className="link" onClick={() => { setOrg(null); setStep("org"); }}>Switch org</button>
            )}
            <button className="link" onClick={logout}>Log out</button>
          </span>
        )}
      </header>
      {step === "login" && (
        <Login onDone={(s) => { setSession(s); setStep("org"); }} />
      )}
      {step === "org" && <OrgPicker orgs={session.organizations} onPick={pickOrg} />}
      {step === "diagnostic" && <Diagnostic onDone={() => setStep("report")} />}
      {step === "report" && <Report onRetake={() => setStep("diagnostic")} />}
      {step === "dashboard" && <Dashboard />}
    </div>
  );
}
