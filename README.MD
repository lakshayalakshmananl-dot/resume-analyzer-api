# Resume Analyzer API

An AI-powered resume analysis API built with FastAPI, PostgreSQL, and Groq LLM. Upload a PDF resume, provide a job description, and get an instant match score with skill gap analysis.

## Live URL

https://resume-analyzer-api-production-4a17.up.railway.app/docs

## Tech Stack

- **Backend**: FastAPI, Python 3.14
- **Database**: PostgreSQL (Railway)
- **AI/LLM**: Groq API (llama-3.3-70b-versatile)
- **Auth**: JWT (python-jose + bcrypt)
- **Deployment**: Railway

## Setup Guide

### 1. Clone the repo
```bash
git clone https://github.com/lakshayalakshmananl-dot/resume-analyzer-api.git
cd resume-analyzer-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```env
DATABASE_URL=postgresql://user:password@localhost:5432/resume_analyzer
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

### 4. Run database migrations
```bash
alembic upgrade head
```

### 5. Start the server
```bash
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret (min 32 chars) |
| `ALGORITHM` | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes |
| `GROQ_API_KEY` | Groq API key from console.groq.com |

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/users/register` | Register a new user | No |
| POST | `/users/login` | Login and get JWT token | No |
| GET | `/users/me` | Get current user info | Yes |
| POST | `/resumes/upload` | Upload a PDF resume | Yes |
| GET | `/resumes/` | List resumes (paginated) | Yes |
| GET | `/resumes/{id}` | Get a single resume | Yes |
| DELETE | `/resumes/{id}` | Delete a resume | Yes |
| POST | `/analyses/` | Analyze resume vs job description | Yes |
| GET | `/analyses/` | List analyses (paginated) | Yes |
| GET | `/analyses/{id}` | Get a single analysis | Yes |
| DELETE | `/analyses/{id}` | Delete an analysis | Yes |

## Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Coverage: 81%

## Features

- JWT authentication (register, login, protected routes)
- PDF upload and text extraction with pdfplumber
- AI resume scoring via Groq LLM (llama-3.3-70b-versatile)
- Skill gap analysis (matched skills, missing skills, suggestions)
- Paginated list endpoints with skip/limit
- Input validation with Pydantic
- 81% test coverage with pytest