import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fixOutput, setFixOutput] = useState(null);

  async function analyze() {
    if (!file) return setError("Please choose a log file first.");
    setLoading(true);
    setError("");
    setFixOutput(null);
    try {
      const fd = new FormData();
      fd.append("logfile", file);
      const res = await fetch("/api/analyze", { method: "POST", body: fd });
      const data = await res.json();
      if (data.error) setError(data.error);
      setResult(data.error ? null : data);
    } catch (e) {
      setError("Could not reach the server.");
    } finally {
      setLoading(false);
    }
  }

  async function remediate(service) {
    const res = await fetch("/api/remediate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service }),
    });
    setFixOutput(await res.json());
  }

  const maxErrors = result ? Math.max(1, ...result.anomalies.map((a) => a.errors)) : 1;

  return (
    <div className="container">
      <h1>LogSense AI</h1>
      <p className="muted">
        Upload a Linux server log. An Isolation Forest model flags unusual minutes and suggests a fix.
      </p>

      <div className="row">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={analyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="cards">
            <div className="card"><b>{result.parsed_lines}</b><span>Lines parsed</span></div>
            <div className="card"><b>{result.minutes_analyzed}</b><span>Minutes analyzed</span></div>
            <div className="card bad"><b>{result.anomaly_count}</b><span>Anomalies</span></div>
          </div>

          <h2>Detected anomalies</h2>
          <table>
            <thead>
              <tr><th>Minute</th><th>Errors</th><th>Failures</th><th>Score</th><th>Suspect</th><th>Action</th></tr>
            </thead>
            <tbody>
              {result.anomalies.map((a) => (
                <tr key={a.minute}>
                  <td>{a.minute}</td>
                  <td>
                    <div className="bar" style={{ width: `${(a.errors / maxErrors) * 100}%` }} />
                    {a.errors}
                  </td>
                  <td>{a.failures}</td>
                  <td>{a.score}</td>
                  <td>{a.suspect_service || "-"}</td>
                  <td>
                    {a.suspect_service ? (
                      <button onClick={() => remediate(a.suspect_service)}>Remediate (dry run)</button>
                    ) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {fixOutput && <pre>{JSON.stringify(fixOutput, null, 2)}</pre>}
    </div>
  );
}
