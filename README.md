# 🔍 LogSense AI

**AI-powered log analysis for Linux servers.** LogSense AI parses server logs, uses machine learning (**Isolation Forest**) to detect anomalous minutes, and suggests or triggers an **Ansible** remediation for the failing service, all from a clean React dashboard.

---

## 📌 Project Overview

Server logs are huge and noisy, and incidents are easy to miss. LogSense AI groups logs per minute, extracts numeric features, and uses unsupervised learning to flag unusual spikes of errors, warnings and failures. It then identifies the service responsible and offers a safe, dry-run-by-default fix.

---

## ✨ Features

- Log parser with **per-minute feature extraction** (total logs, errors, warnings, failure keywords, distinct services)
- **Unsupervised anomaly detection** using scikit-learn `IsolationForest`
- **Flask REST API** for analysis and remediation
- **React (Vite) dashboard**: upload logs, view anomaly cards and table, trigger remediation
- **Ansible playbook** to restart the suspect service (**dry-run by default**, apply with `REMEDIATE=1`)
- **Security-conscious remediation**: service names are allow-listed and never passed raw to a shell
- **Docker** multi-stage build, **Kubernetes** manifest (2 replicas, readiness probe) and **GitHub Actions CI**
- Sample log generator with an injected incident for quick demos
- Automated tests with Pytest

---

## 🛠️ Tech Stack

| Area | Technology |
|------|------------|
| Backend | Python 3.11, Flask, Gunicorn |
| Machine Learning | scikit-learn (Isolation Forest), pandas |
| Frontend | React 18, Vite |
| Automation | Ansible |
| DevOps | Docker, Kubernetes, GitHub Actions |
| Testing | Pytest |

---

## 📂 Project Structure

```text
LogSense-AI/
├── app.py                   # Flask API + serves the built dashboard
├── analyzer.py              # Log parsing, features, anomaly detection
├── generate_sample_log.py   # Creates sample.log with an injected incident
├── frontend/                # React (Vite) dashboard
│   └── src/ (App.jsx, main.jsx, styles.css)
├── templates/index.html     # Fallback page if the dashboard is not built
├── ansible/remediate.yml    # Restart-service playbook
├── k8s/deployment.yaml      # Deployment + Service
├── tests/test_analyzer.py
├── .github/workflows/ci.yml # Tests + Docker build
├── Dockerfile
└── requirements.txt
```

---

## 🧠 How It Works

1. **Parse**: read lines in the format `YYYY-MM-DD HH:MM:SS LEVEL service message` and skip invalid lines.
2. **Group** the logs per minute.
3. **Extract features** per minute: total logs, errors, warnings, failure keywords (`failed`, `denied`, `refused`) and number of distinct services.
4. **Detect**: Isolation Forest scores each minute, and the lowest scores are flagged as anomalies.
5. **Suggest a fix**: the service with the most errors in a flagged minute is recommended for an Ansible restart.

**Log format example**

```text
2026-10-01 10:02:11 ERROR nginx Upstream timed out
```

Levels: `INFO`, `WARN`, `ERROR`, `CRITICAL`. At least 10 minutes of parsable logs are needed.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/health` | Health check |
| POST | `/api/analyze` | Upload a log file (`logfile`) or raw text and get anomalies |
| POST | `/api/remediate` | Run the Ansible playbook for a service (`nginx`, `mysql`, `sshd`, `app`) |

```bash
# Analyze a log file
curl -X POST http://localhost:5000/api/analyze -F "logfile=@sample.log"

# Dry-run remediation
curl -X POST http://localhost:5000/api/remediate \
  -H "Content-Type: application/json" \
  -d '{"service": "nginx"}'
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Ansible, Docker, kubectl

### Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/LogSense-AI.git
cd LogSense-AI

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Generate a sample log with an injected incident
python generate_sample_log.py

# 4. Start the API (http://localhost:5000)
python app.py

# 5. Start the dashboard in another terminal (http://localhost:5173)
cd frontend
npm install
npm run dev
```

To serve the dashboard from Flask instead, run `npm run build` inside `frontend/` and open **http://localhost:5000**.

### Run Tests

```bash
pytest -q
```

### Docker

```bash
docker build -t logsense-ai .
docker run -p 5000:5000 logsense-ai
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

---

## 🔒 Safety Notes

- Remediation runs in **dry-run (`--check`) mode by default**. Set `REMEDIATE=1` to actually restart a service.
- Only **allow-listed service names** are accepted.
- The playbook needs Ansible installed and sufficient privileges on the target host.

---

## ⚠️ Limitations

- Fixed log format and a small feature set
- Unsupervised detection can produce false positives
- Remediation only restarts services

---

## 🚀 Future Improvements

- Real syslog / journald parsing
- Alerting (email, Slack)
- Model retraining on historical data
- More remediation actions
- Authentication for the API

---

## 👩‍💻 Author

**Riya Yadav**

🎓 B.Tech CSE (Final Year) | 💼 Aspiring Software Developer

🔗 [LinkedIn](https://www.linkedin.com/in/riyayadav0803/)

---

## ⭐ Support

If you found this project helpful, please consider giving it a **star**!
