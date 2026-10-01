"""Log parsing + ML anomaly detection for LogSense AI."""
import re
from collections import Counter, defaultdict

import pandas as pd
from sklearn.ensemble import IsolationForest

# Log format: 2026-10-01 10:02:11 ERROR nginx Upstream timed out
LOG_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}\s+"
    r"(?P<level>INFO|WARN|ERROR|CRITICAL)\s+(?P<service>\S+)\s+(?P<msg>.*)$"
)


def parse_logs(text):
    """Turn raw log text into a DataFrame. Unparseable lines are skipped."""
    rows = []
    for line in text.splitlines():
        m = LOG_RE.match(line.strip())
        if m:
            rows.append(m.groupdict())
    return pd.DataFrame(rows, columns=["ts", "level", "service", "msg"])


def build_features(df):
    """Aggregate logs into one row of numeric features per minute."""
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["is_err"] = df["level"].isin(["ERROR", "CRITICAL"]).astype(int)
    df["is_warn"] = (df["level"] == "WARN").astype(int)
    df["is_fail"] = df["msg"].str.contains("failed|denied|refused", case=False).astype(int)
    g = df.groupby("ts")
    feats = pd.DataFrame({
        "total": g.size(),
        "errors": g["is_err"].sum(),
        "warnings": g["is_warn"].sum(),
        "failures": g["is_fail"].sum(),
        "services": g["service"].nunique(),
    })
    return feats


def top_failing_service(df, minute):
    """Service with the most errors in a given minute (used for remediation hints)."""
    sub = df[(df["ts"] == minute) & (df["level"].isin(["ERROR", "CRITICAL"]))]
    if sub.empty:
        return None
    return Counter(sub["service"]).most_common(1)[0][0]


def detect_anomalies(text, contamination=0.05):
    """Return a dict with summary stats and the list of anomalous minutes."""
    df = parse_logs(text)
    feats = build_features(df)
    if len(feats) < 10:
        return {"error": "Need at least 10 minutes of parsable logs.", "parsed_lines": len(df)}

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(feats)
    feats["score"] = model.decision_function(feats)
    feats["anomaly"] = model.predict(feats[["total", "errors", "warnings", "failures", "services"]]) == -1

    anomalies = []
    for minute, row in feats[feats["anomaly"]].sort_values("score").iterrows():
        svc = top_failing_service(df, minute)
        anomalies.append({
            "minute": minute,
            "score": round(float(row["score"]), 3),
            "errors": int(row["errors"]),
            "failures": int(row["failures"]),
            "total": int(row["total"]),
            "suspect_service": svc,
            "suggestion": f"Restart '{svc}' via Ansible" if svc else "Investigate manually",
        })
    return {
        "parsed_lines": len(df),
        "minutes_analyzed": len(feats),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }
