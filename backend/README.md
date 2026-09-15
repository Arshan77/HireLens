# HireLens Backend — Phase 1 & Phase 2 Complete Engine

HireLens is an AI-powered resume analyzer and job matcher. 

* **Phase 1**: Core backend foundation and file parsing pipeline (`.pdf`/`.docx`).
* **Phase 2**: Explainable NLP & Matching Analysis Engine (Skill Extraction, Taxonomy Mapping, TF-IDF Cosine Similarity, Experience & Education Alignment, ATS Quality Checking, and Composite Scoring).

---

## Features

### Phase 1: Foundation & Parsing Pipeline
* **Health Check Endpoints**: `/` and `/api/v1/health`.
* **Resume Upload & Parsing**: `POST /api/v1/resumes/upload` accepting PDF and DOCX files up to 5 MB.
* **Security & Validation**: Extension whitelist, MIME type verification, magic-byte checking (`%PDF-` for PDF, `PK\x03\x04` for DOCX), and path traversal prevention.
* **Extraction & Normalization**: Layout-aware text extraction and whitespace/newline cleaning.
* **Section Parser**: Heuristic detection for `contact`, `summary`, `skills`, `experience`, `education`, `projects`, and `certifications`.

### Phase 2: Explainable NLP & Matching Analysis Engine
* **Skill Taxonomy & Normalization**: Canonical taxonomy mapping aliases (e.g. `postgres`, `pgsql` -> `PostgreSQL`; `react.js`, `reactjs` -> `React`).
* **Boundary-Aware Skill Extraction**: Prevents false positive substring matches (e.g. isolated `C` or `Go` vs words like `communication` or `ongoing`).
* **Job Description Analyzer**: Categorizes requirements into `required_skills` and `preferred_skills`.
* **Skill Coverage Overlap Matcher**: Computes required (80% weight) and preferred (20% weight) skill coverage percentages.
* **Text Similarity Engine**: Computes TF-IDF Vector Space Model & Cosine Similarity between resume and job description text.
* **Experience Alignment Checker**: Deterministically extracts required vs. candidate experience years and evaluates alignment.
* **Education Alignment Checker**: Extracts and compares degree ranks (`Bachelor's`, `Master's`, `Doctorate`).
* **ATS Quality Health Analyzer**: Checks section completeness (50%), action verb density (25%), and quantifiable metric occurrences (25%).
* **Composite Weighted Scoring**: Combines all sub-scores into an explainable 0–100 overall score.
* **Stateless Preview API Endpoint**: `POST /api/v1/analysis/preview`.

---

## Architecture & Service Structure

```text
backend/app/
├── core/
│   ├── config.py              # Application settings & limits
│   └── exceptions.py          # Custom FileValidationError & FileExtractionError
├── schemas/
│   ├── resume.py              # Phase 1 response models
│   └── analysis.py            # Phase 2 Pydantic schemas (AnalysisPreviewResponse, sub-scores)
├── services/
│   ├── validator.py           # File security & magic-byte validator
│   ├── extractor.py           # PyMuPDF & python-docx text extractor
│   ├── cleaner.py             # Whitespace & unicode cleaner
│   ├── section_parser.py      # Heuristic section parser
│   ├── skill_taxonomy.py      # Master canonical skill taxonomy dictionary
│   ├── skill_extractor.py     # Boundary-aware regex skill extractor
│   ├── jd_analyzer.py         # JD required vs preferred skill parser
│   ├── skill_matching.py      # Skill coverage overlap matcher & score calculator
│   ├── text_similarity.py     # TF-IDF Cosine Similarity engine
│   ├── experience_analyzer.py # Rule-based experience years aligner
│   ├── education_analyzer.py  # Rule-based degree rank aligner
│   ├── ats_analyzer.py        # ATS health analyzer (sections, verbs, metrics)
│   ├── scoring.py             # Composite score aggregator
│   └── analysis_engine.py     # Engine pipeline orchestrator
└── routers/
    ├── health.py              # Health check endpoints
    ├── resumes.py             # Resume upload router
    └── analysis.py            # Stateless analysis preview endpoint
```

---

## Mathematical Scoring Methodology

$$\text{Overall Score} = (0.40 \times S_{\text{skill}}) + (0.30 \times S_{\text{text}}) + (0.15 \times S_{\text{exp}}) + (0.15 \times S_{\text{ats}})$$

### 1. Skill Match Score ($S_{\text{skill}}$) — Weight: 40%
$$\text{Required Coverage} = \frac{|R \cap J_{\text{required}}|}{|J_{\text{required}}|} \times 100$$
$$\text{Preferred Coverage} = \frac{|R \cap J_{\text{preferred}}|}{|J_{\text{preferred}}|} \times 100$$
$$S_{\text{skill}} = (0.80 \times \text{Required Coverage}) + (0.20 \times \text{Preferred Coverage})$$

### 2. Text Similarity Score ($S_{\text{text}}$) — Weight: 30%
TF-IDF sparse vector representations $V_{\text{resume}}$ and $V_{\text{jd}}$ are compared via Cosine Similarity:
$$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
$$S_{\text{text}} = \text{Cosine Similarity}(V_{\text{resume}}, V_{\text{jd}}) \times 100$$

### 3. Experience Alignment Score ($S_{\text{exp}}$) — Weight: 15%
* **Aligned / Exceeds Requirement**: $100\%$
* **Below Requirement**: $\frac{\text{Candidate Years}}{\text{Required Years}} \times 100\%$
* **Entry-Level / Fresher Job**: $100\%$

### 4. ATS Quality Score ($S_{\text{ats}}$) — Weight: 15%
$$S_{\text{ats}} = (0.50 \times \text{Section Completeness}) + (0.25 \times \text{Action Verb Ratio}) + (0.25 \times \text{Metrics Ratio})$$

---

## API Endpoints

### 1. Stateless Analysis Preview Endpoint
`POST /api/v1/analysis/preview`

#### Example Request Body
```json
{
  "resume_text": "Alex Mercer\nEmail: alex@example.com\nSUMMARY\nSoftware engineer with 2 years experience.\nSKILLS\nPython, FastAPI, React, PostgreSQL, Docker\nWORK EXPERIENCE\nEngineered RESTful APIs with FastAPI reducing latency by 35%.\nEDUCATION\nB.S. in Computer Science",
  "job_description_text": "Seeking Python Backend Developer with FastAPI and PostgreSQL skills. 2+ years experience required."
}
```

#### Example Response Body
```json
{
  "overall_score": 81.1,
  "score_breakdown": {
    "skill_score": 100.0,
    "text_similarity_score": 45.2,
    "experience_score": 100.0,
    "ats_quality_score": 83.3
  },
  "weights": {
    "skill": 0.4,
    "text_similarity": 0.3,
    "experience": 0.15,
    "ats": 0.15
  },
  "resume_skills": ["Docker", "FastAPI", "PostgreSQL", "Python", "React"],
  "required_jd_skills": ["FastAPI", "PostgreSQL", "Python"],
  "preferred_jd_skills": [],
  "matching_skills": ["FastAPI", "PostgreSQL", "Python"],
  "missing_required_skills": [],
  "missing_preferred_skills": [],
  "recommendations": [
    "Include quantifiable numbers and metrics (e.g. 'improved performance by 30%', '500+ users') to demonstrate impact."
  ],
  "warnings": []
}
```

---

## Setup & Running Test Suite

```bash
# Navigate to backend directory
cd backend

# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run complete test suite (72 tests)
pytest -v
```

---

## Technical Accuracy Notice

* **Explainable Analysis**: HireLens uses open, deterministic mathematics and lexical TF-IDF cosine similarity. It does not treat evaluation as an opaque black box.
* **ATS Best-Practice Checker**: The ATS quality module checks standard formatting heuristics (sections, action verbs, metrics). It is a best-practice guideline checker, not a clone of proprietary commercial ATS systems.
