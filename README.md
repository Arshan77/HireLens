# HireLens — AI-Powered Resume Analyzer & Job Matcher

HireLens is a full-stack, transparent, and explainable resume analysis platform designed for job seekers, graduates, and professionals. Unlike opaque black-box AI tools, HireLens uses a hybrid deterministic and NLP-driven matching engine that produces clear, mathematically grounded scores:

- **40% Skill Match**: Required vs. preferred technical skills evaluated against an extensive domain taxonomy.
- **30% Normalized Term-Frequency Cosine Similarity**: Evaluates textual and vocabulary similarity while remaining robust across document length variations.
- **15% Experience & Education Alignment**: Rule-based degree level and years-of-experience verification against job requirements.
- **15% ATS Health**: Structural section completeness, action verb density, and quantifiable metric checks.

---

## Key Features

1. **Deterministic Matching Engine**:
   - Transparent, explainable scoring breakdown (Overall, Skill, Text Similarity, Experience/Education, ATS).
   - Dynamic skill taxonomy covering 140+ tech skills across Frontend, Backend, Data, and AI/ML roles.
   - Comprehensive role recommendation ranking based strictly on extracted candidate skills.

2. **Persistent Analyses & User Isolation**:
   - Secure JWT-based authentication with bcrypt password hashing (enforcing 72-byte truncation safety).
   - Strict server-side ownership enforcement on all uploaded resumes, job descriptions, and analyses.

3. **PDF Report Generation (Phase 6)**:
   - High-fidelity, publication-grade PDF report export generated on-demand via `reportlab`.
   - Uses stored analysis data directly without rerunning compute-intensive matching.
   - Authenticated and strictly user-isolated (`GET /api/v1/analysis/{analysis_id}/report`).
   - Clean, professional formatting including executive summary, radar/metric breakdowns, matched vs. missing skills, prioritized gaps, and unified recommendations.

4. **Production Configuration & Security**:
   - Environment-driven configuration (`ENVIRONMENT=development` vs `ENVIRONMENT=production`).
   - Production validation: enforces strong cryptographic `JWT_SECRET_KEY` and rejects wildcard CORS origins.
   - SQLite development fallback and managed PostgreSQL production readiness via Alembic migrations.
   - API documentation Swagger/ReDoc automatically disabled in production mode.

---

## Technology Stack

- **Backend**:
  - Python 3.11+
  - FastAPI
  - Pydantic v2
  - SQLAlchemy 2.0 & Alembic
  - PyMuPDF & python-docx
  - scikit-learn & NumPy
  - ReportLab 4.x/5.x
  - SQLite (Local Dev) / PostgreSQL (Production)

- **Frontend**:
  - React 18
  - Vite
  - Tailwind CSS
  - React Router v6
  - Lucide React Icons
  - Recharts

---

## Project Structure

```
HireLens/
├── backend/
│   ├── alembic/                 # Database schema migrations
│   ├── app/
│   │   ├── core/                # Configuration, JWT security, exceptions
│   │   ├── db/                  # Database session & engine
│   │   ├── models/              # SQLAlchemy models (User, Resume, JobDescription, Analysis)
│   │   ├── repositories/        # Database access layers
│   │   ├── routers/             # FastAPI routers (auth, resumes, analysis, health)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Matching engine, parser, taxonomy, PDF generator
│   │   └── main.py              # Application entry point
│   ├── tests/                   # Pytest automated test suite (117 tests)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API clients
│   │   ├── components/          # Reusable UI components
│   │   ├── context/             # AuthContext state
│   │   ├── pages/               # Landing, Auth, Upload, Analyze, Results, History
│   │   └── __tests__/           # Vitest frontend tests (15 tests)
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── PROJECT_PLAN.md
└── README.md
```

---

## Local Development Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env

# Run database migrations
alembic upgrade head

# Start development server on port 8001
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env

# Start Vite development server
npm run dev
```

---

## Verification & Testing Commands

### Backend Test Suite
```bash
cd backend
.\.venv\Scripts\pytest -v
# Output: 117 passed, 3 warnings
```

### Frontend Test Suite
```bash
cd frontend
npm test -- --run
# Output: 4 test suites passed, 15 tests passed
```

### Frontend Production Build
```bash
cd frontend
npm run build
# Output: dist/ bundle created cleanly
```

### Live PDF Download Verification
```bash
cd backend
.\.venv\Scripts\python tests\verify_live_pdf_download.py
# Output: Verified authenticated download, %PDF- binary header, 401 unauth guard, 404 isolation
```

---

## Production Deployment Preparation

1. **Frontend**:
   - Host as static files (Vercel, Netlify, Cloudflare Pages, AWS S3/CloudFront).
   - Set environment variable: `VITE_API_URL=https://api.yourdomain.com`.

2. **Backend**:
   - Deploy as containerized FastAPI service (Render, Railway, Fly.io, AWS ECS, Google Cloud Run).
   - Set environment variables:
     - `ENVIRONMENT=production`
     - `DEBUG=False`
     - `PORT=8000` (or platform standard)
     - `DATABASE_URL=postgresql+psycopg://user:password@host:5432/hirelens_db`
     - `JWT_SECRET_KEY=<generate-strong-random-secret-key>`
     - `CORS_ORIGINS=https://hirelens.yourdomain.com`

3. **Database**:
   - Managed PostgreSQL (Neon, Supabase, AWS RDS, Railway Postgres).
   - Run `alembic upgrade head` during deployment build/release phase.
