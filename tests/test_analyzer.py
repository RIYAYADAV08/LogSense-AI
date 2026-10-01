import subprocess
import sys

from analyzer import detect_anomalies, parse_logs


def test_parse_skips_bad_lines():
    df = parse_logs("2026-10-01 10:00:01 INFO nginx ok\nnot a log line")
    assert len(df) == 1


def test_detects_injected_incident():
    subprocess.run([sys.executable, "generate_sample_log.py"], check=True)
    result = detect_anomalies(open("sample.log").read())
    minutes = [a["minute"] for a in result["anomalies"]]
    assert "2026-10-01 10:41" in minutes or "2026-10-01 10:42" in minutes


def test_too_little_data():
    assert "error" in detect_anomalies("2026-10-01 10:00:01 INFO nginx ok")
