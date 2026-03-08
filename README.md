# Lead Generation System

A scalable platform that extracts business leads from **Google Maps**, crawls business websites, extracts & validates emails, and stores them in **MongoDB**.

**Target output:** 1,000–5,000 verified emails per day.

---

## Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Backend     | Python, FastAPI, AsyncIO            |
| Scraping    | httpx, BeautifulSoup, Playwright    |
| Queue       | Redis, Celery                       |
| Database    | MongoDB (Motor async driver)        |
| APIs        | Google Places API, Geocoding API    |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Google Maps API key, MongoDB URI, Redis URL
```

### 3. Start services

```bash
# MongoDB (must be running)
mongod

# Redis (must be running)
redis-server

# FastAPI server
uvicorn app.main:app --reload --port 8000

# Celery worker (in a separate terminal)
celery -A app.celery_app worker --loglevel=info -Q lead_generation,grid,search,details,crawl,email
```

### 4. Use the API

Open Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

| Method | Path                       | Description                              |
|--------|----------------------------|------------------------------------------|
| POST   | `/api/v1/start-search`     | Start Google Maps search for a city      |
| POST   | `/api/v1/start-scraping`   | Trigger website crawl + email extraction |
| GET    | `/api/v1/leads`            | Paginated leads list                     |
| GET    | `/api/v1/stats`            | Database statistics                      |
| GET    | `/api/v1/export?format=csv`| Export leads as CSV or JSON              |

### Example: Start a search

```bash
curl -X POST http://localhost:8000/api/v1/start-search \
  -H "Content-Type: application/json" \
  -d '{"city": "Delhi", "keywords": ["dentist", "restaurant"]}'
```

---

## Pipeline

```
City Grid Generator → Keyword Expansion → Google Maps Search
    → Place Details → Website Discovery → Website Crawler
    → Email Extraction → Email Validation → MongoDB Storage
```

Each stage runs as an async Celery task with retry logic and rate limiting.

---

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Settings from .env
├── database.py          # MongoDB connection (Motor)
├── celery_app.py        # Celery + Redis setup
├── models/
│   ├── business.py      # Business document model
│   └── email.py         # Email document model
├── modules/
│   ├── grid_generator.py
│   ├── keyword_engine.py
│   ├── maps_search.py
│   ├── place_details.py
│   ├── website_discovery.py
│   ├── website_crawler.py
│   ├── email_extractor.py
│   ├── email_pattern.py
│   └── email_validator.py
├── tasks/
│   └── pipeline.py      # Celery task definitions
├── api/
│   └── routes.py        # FastAPI endpoints
└── utils/
    └── rate_limiter.py   # Token-bucket rate limiter
```
