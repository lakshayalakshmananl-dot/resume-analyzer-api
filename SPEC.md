# Resume Analyzer API — Capstone Specification

## Overview

A FastAPI-based REST API that allows users to upload PDF resumes, extract text, and score
them against a job description using an LLM (via HuggingFace Inference API). Returns a
structured analysis including match score, skill gap report, and improvement suggestions.

---

## Features List

### Core Features
- User registration and JWT-based authentication
- Upload PDF resume (stored locally or S3-compatible path)
- Extract raw text from uploaded PDF
- Store resumes with metadata per user
- Submit a job description (JD) for comparison
- LLM-powered scoring of resume vs JD (0–100 score + rationale)
- Skill gap analysis — matched skills, missing skills, bonus skills
- Store and retrieve past analysis results per user
- Paginated list endpoints for resumes and analyses

### AI/ML Feature
- **LLM Inference via HuggingFace Inference API** (model: `mistralai/Mistral-7B-Instruct-v0.2`)
- Prompt engineering to extract structured JSON output: score, matched skills, missing skills, suggestions
- Fallback: `facebook/bart-large-mnli` for zero-shot classification if LLM quota exceeded

---

## Database Models

### 1. `users`
| Field        | Type         | Constraints                  |
|--------------|--------------|------------------------------|
| id           | UUID         | PK, default uuid4            |
| email        | VARCHAR(255) | UNIQUE, NOT NULL             |
| username     | VARCHAR(100) | UNIQUE, NOT NULL             |
| hashed_password | VARCHAR(255) | NOT NULL                |
| is_active    | BOOLEAN      | DEFAULT TRUE                 |
| created_at   | TIMESTAMP    | DEFAULT now()                |

### 2. `resumes`
| Field        | Type         | Constraints                       |
|--------------|--------------|-----------------------------------|
| id           | UUID         | PK, default uuid4                 |
| user_id      | UUID         | FK → users.id, NOT NULL           |
| filename     | VARCHAR(255) | NOT NULL                          |
| file_path    | VARCHAR(500) | NOT NULL                          |
| extracted_text | TEXT       | nullable (populated after parse)  |
| upload_date  | TIMESTAMP    | DEFAULT now()                     |

### 3. `analyses`
| Field           | Type         | Constraints                    |
|-----------------|--------------|--------------------------------|
| id              | UUID         | PK, default uuid4              |
| resume_id       | UUID         | FK → resumes.id, NOT NULL      |
| user_id         | UUID         | FK → users.id, NOT NULL        |
| job_description | TEXT         | NOT NULL                       |
| job_title       | VARCHAR(255) | nullable                       |
| score           | INTEGER      | 0–100, NOT NULL                |
| matched_skills  | JSON         | list of strings                |
| missing_skills  | JSON         | list of strings                |
| suggestions     | JSON         | list of strings                |
| raw_llm_output  | TEXT         | full LLM response (debug)      |
| created_at      | TIMESTAMP    | DEFAULT now()                  |

---

## API Endpoints

### Auth
| Method | Path                | Description                        |
|--------|---------------------|------------------------------------|
| POST   | /auth/register      | Register a new user                |
| POST   | /auth/login         | Login, returns JWT access token    |
| GET    | /auth/me            | Get current authenticated user     |

### Resumes
| Method | Path                    | Description                              |
|--------|-------------------------|------------------------------------------|
| POST   | /resumes/upload         | Upload PDF resume, triggers text extract |
| GET    | /resumes/               | List all resumes for current user        |
| GET    | /resumes/{resume_id}    | Get resume metadata + extracted text     |
| DELETE | /resumes/{resume_id}    | Delete a resume and its analyses         |

### Analyses
| Method | Path                          | Description                               |
|--------|-------------------------------|-------------------------------------------|
| POST   | /analyses/                    | Submit JD against a resume → run LLM     |
| GET    | /analyses/                    | List all analyses for current user        |
| GET    | /analyses/{analysis_id}       | Get a specific analysis result            |
| DELETE | /analyses/{analysis_id}       | Delete an analysis                        |

### Health
| Method | Path     | Description              |
|--------|----------|--------------------------|
| GET    | /        | Root health check        |
| GET    | /health  | DB + LLM connectivity   |

---

## AI/ML Integration Detail

**Endpoint:** `POST /analyses/`

**Flow:**
1. Accept `resume_id` + `job_description` + optional `job_title`
2. Fetch extracted resume text from DB
3. Build prompt:
```
You are an expert technical recruiter. Analyze the resume below against the job description.
Return ONLY valid JSON with keys: score (int 0-100), matched_skills (list), missing_skills (list), suggestions (list of 3 actionable items).

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
```
4. Call HuggingFace Inference API with Mistral-7B
5. Parse JSON from LLM response
6. Store result in `analyses` table
7. Return structured `AnalysisResponse`

---

## Project Structure

```
resume-analyzer-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── resume.py
│   │   └── analysis.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── resume.py
│   │   └── analysis.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── resumes.py
│   │   └── analyses.py
│   ├── services/
│   │   ├── pdf_extractor.py
│   │   └── llm_service.py
│   └── core/
│       ├── security.py
│       └── dependencies.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── tests/
│   ├── test_auth.py
│   ├── test_resumes.py
│   └── test_analyses.py
├── uploads/               # local PDF storage
├── alembic.ini
├── requirements.txt
├── .env.example
├── README.md
└── SPEC.md
```

---

## Tech Stack

| Layer       | Tool/Library                              |
|-------------|-------------------------------------------|
| Framework   | FastAPI + Uvicorn                         |
| ORM         | SQLAlchemy 2.0 (async)                   |
| Migrations  | Alembic                                   |
| Database    | PostgreSQL 15                             |
| Auth        | python-jose (JWT) + passlib (bcrypt)      |
| PDF Parse   | pdfplumber                                |
| LLM         | HuggingFace Inference API (Mistral-7B)    |
| Validation  | Pydantic v2                               |
| Testing     | pytest + httpx + pytest-asyncio           |
| Deployment  | Railway (PostgreSQL add-on)               |
| Env Vars    | python-dotenv                             |