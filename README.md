# 🔍 AI-Based OSINT Correlation & Social Engineering Exposure Analysis System

A professional cybersecurity web application that demonstrates how publicly available information (OSINT) can be analyzed and correlated using AI to assess social engineering exposure risks.

> ⚠️ **CEH-Compliant** — Educational and defensive use only. No private data access, no identity confirmation, no surveillance.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py

# 3. Open in browser
# http://localhost:8000
```

---

## 🔬 Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Image Analysis** | Face detection, perceptual hashing, cross-platform image reuse detection |
| 👤 **Username Correlation** | Pattern matching, alias generation, cross-platform search simulation |
| 🔗 **OSINT Correlation** | Multi-modal data fusion combining image + username intelligence |
| ⚔️ **Attack Vector Assessment** | Evaluates feasibility of pretexting, spear-phishing, impersonation |
| 🌐 **Cross-Platform Aggregation** | Combines data from multiple platforms into unified exposure view |
| 🛡️ **Defensive Recommendations** | Actionable steps to reduce social engineering exposure |
| 📊 **Risk Scoring** | Quantified risk scores with visual gauges and breakdowns |

---

## 🏗️ Architecture

```
User Browser → Frontend (HTML/CSS/JS)
                    ↓
              Backend API (FastAPI)
                    ↓
         AI & OSINT Analysis Engine
          ├── Image Analyzer (OpenCV)
          ├── Username Analyzer (NLP)
          ├── Correlation Engine
          └── Risk Assessor
                    ↓
           CEH-Safe Output Report
```

---

## 💻 Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI/ML**: OpenCV, ImageHash, Scikit-learn, NLP algorithms
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Security**: Input validation, rate limiting, CORS, no persistent storage

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check |
| `POST` | `/api/analyze/image` | Image similarity analysis |
| `POST` | `/api/analyze/username` | Username correlation analysis |
| `POST` | `/api/analyze/full` | Full OSINT correlation + risk report |
| `GET` | `/docs` | Interactive API documentation (Swagger) |

---

## 🛡️ Ethical & Legal Compliance

- ✅ Uses only simulated public OSINT data
- ✅ No private data scraping
- ✅ No biometric identity confirmation
- ✅ No data monetization or storage
- ✅ Fully aligned with CEH Code of Ethics
- ✅ Educational and defensive purpose only

---

## 📋 Project Structure

```
OSINT-Analysis-System/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md
├── engine/
│   ├── __init__.py
│   ├── image_analyzer.py   # AI image analysis
│   ├── username_analyzer.py # Username correlation
│   ├── correlation_engine.py # Data fusion
│   └── risk_assessor.py    # Risk assessment
└── static/
    ├── index.html           # Main UI
    ├── css/
    │   └── styles.css       # Cybersecurity theme
    └── js/
        └── app.js           # Frontend logic
```
