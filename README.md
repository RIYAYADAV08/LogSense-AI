# LogSense AI

AI-powered log analysis tool for Linux servers. It parses server logs, uses machine learning
(Isolation Forest) to detect anomalous minutes, and suggests or triggers an Ansible remediation.

## Features
- Log parser + per-minute feature extraction (errors, warnings, failures, services)
- Unsupervised anomaly detection with scikit-learn `IsolationForest`
- Flask REST API (`/api/analyze`, `/api/remediate`, `/health`)
- React (Vite) dashboard: upload logs, view anomaly cards/table, trigger dry-run remediation
- Ansible playbook to restart a suspect service (dry-run by default, `REMEDIATE=1` to apply)
- Docker image, Kubernetes manifest, and GitHub Actions CI (tests + docker build)

## Run locally
```bash
pip install -r requirements.txt
python generate_sample_log.py      # creates sample.log with an injected incident
python app.py                      # API on http://localhost:5000
cd frontend && npm install
npm run dev                        # dashboard on http://localhost:5173 (proxies /api to Flask)
# or: npm run build, then Flask serves the built dashboard at http://localhost:5000
pytest -q
```

## Docker / Kubernetes
```bash
docker build -t logsense-ai .
docker run -p 5000:5000 logsense-ai
kubectl apply -f k8s/deployment.yaml
```

## Log format
`YYYY-MM-DD HH:MM:SS LEVEL service message` (LEVEL = INFO / WARN / ERROR / CRITICAL)

## How it works
1. Parse lines and group them per minute.
2. Features per minute: total logs, errors, warnings, failure keywords, distinct services.
3. IsolationForest scores each minute; the lowest scores are flagged as anomalies.
4. The service with the most errors in a flagged minute is suggested for an Ansible restart.

## Limitations / future work
- Fixed log format, small feature set, unsupervised so false positives are possible
- Remediation only restarts services; allow-listed service names only
- Ideas: real syslog parsing, alerting, model retraining on historical data
