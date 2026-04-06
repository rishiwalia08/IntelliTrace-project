# CipherLink

A real-time fraud intelligence platform for Supply Chain Finance (SCF) that detects risky invoices before banks disburse funds.

## 🚀 Overview

CipherLink helps lenders and enterprises stop invoice fraud early by combining invoice validation, relationship graph analytics, and explainable risk scoring in one decision engine.

## ❗ Problem

SCF fraud is often hidden across tiers (Tier 1 → Tier 2 → Tier 3). In one widely cited scenario, hundreds of invoices looked valid one-by-one, but were fraudulent when viewed as a network.

Common fraud types:
- Double financing (same claim funded twice)
- Phantom invoices (fabricated trades)
- Carousel trades (circular trading loops)
- Dilution and abnormal collection behavior

Traditional checks fail because they are document-level, not network-level.

## 💡 Solution

CipherLink turns invoices into decision signals:
1. Ingest invoice + line items with strict validation
2. Generate deterministic invoice fingerprint/hash
3. Block hard duplicates at ingestion
4. Build live supplier-buyer graph from transactions
5. Detect cycles and behavioral anomalies
6. Produce explainable risk score (LOW / MEDIUM / HIGH)

## 🧠 How It Works

### 1) Invoice Ingestion
- API endpoint accepts invoice payload
- Schema validation ensures required fields and valid values
- Data is stored in PostgreSQL via SQLAlchemy

### 2) AI Fingerprinting (Current Rule-Based Foundation)
- Deterministic SHA-256 fingerprint from key fields
- Similarity scoring module estimates near-duplicate risk
- Designed to plug in neural hashing in next phase

### 3) Graph Analysis
- Directed graph: supplier → buyer edges
- Detects circular trades and relationship anomalies
- Flags high-frequency suspicious links and hub anomalies

### 4) Risk Scoring
- Weighted fraud signals converted into a 0–100 score
- Categorized into LOW / MEDIUM / HIGH
- Human-readable reasons generated for underwriting teams

## 🏗️ Architecture Diagram (Text)

```text
[ERP / Upload API]
        |
        v
[FastAPI Ingestion Layer] ---> [Duplicate Check + Hashing]
        |                                  |
        v                                  v
[PostgreSQL: invoices + items]      [Graph Service (NetworkX)]
        |                                  |
        +------------> [Risk Engine] <-----+
                           |
                           v
              [Explainable Fraud Decision API]
                           |
                           v
            [React Dashboard: KPI, Alerts, Graph]
```

## ⚙️ Tech Stack

- Backend: FastAPI, SQLAlchemy 2.x, PostgreSQL
- Graph Analytics: NetworkX
- Frontend: React (Vite), Tailwind CSS, Recharts, react-force-graph-2d
- API Client: Axios
- DevOps: Docker, docker-compose, .env configuration

## 📊 Features

- Deterministic invoice hashing and duplicate prevention
- Graph-based cycle detection (carousel risk)
- Supplier behavior anomaly checks (frequency, velocity, hub patterns)
- Explainable risk scoring with reason trace
- Fraud alert feed for high-risk events
- Interactive graph exploration dashboard

## 🖥️ Screenshots

> Add demo images in this folder and update links below:
- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/invoice-detail-panel.png`
- `docs/screenshots/graph-cycles.png`
- `docs/screenshots/fraud-alerts.png`

## 🚀 Getting Started

### 1) Clone and configure

```bash
git clone <your-repo-url>
cd INTELLITRACE
cp .env.example .env
```

### 2) Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend health:
- `GET http://localhost:8000/api/v1/health`

### 3) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open:
- `http://localhost:5173`

### 4) Docker option

```bash
cd INTELLITRACE
docker compose up --build
```

## 🔮 Future Work

- Dynamic NFT invoice identity on Polygon/Ethereum
- Zero-knowledge proofs for privacy-preserving validation
- Neural document fingerprinting for near-duplicate detection
- GNN-based fraud scoring for deep network intelligence
- Multi-lender shared fraud intelligence protocol

## 📚 Demo & Pitch Assets

- Demo script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- Elevator pitch: [docs/ELEVATOR_PITCH.md](docs/ELEVATOR_PITCH.md)
- Judge Q&A: [docs/JUDGE_QA.md](docs/JUDGE_QA.md)
- Slide deck content: [docs/SLIDE_DECK.md](docs/SLIDE_DECK.md)
