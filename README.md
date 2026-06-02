# Deal Analysis Data Warehouse & AI Pipeline

Pre-cached data warehouse and ingest pipelines for in-house deal-analysis AI.

## Features

- PostgreSQL with PostGIS for spatial data
- ETL pipelines for data ingestion, spatial processing, and validation
- Airflow orchestration for daily pipeline execution
- FastAPI REST API with JWT authentication
- AI integration for deal analysis (OpenAI API)
- Docker Compose for local development

## Tech Stack

- **Database**: PostgreSQL 15 + PostGIS 3
- **ORM**: SQLAlchemy 2.0 + GeoAlchemy2
- **API**: FastAPI + Pydantic
- **Auth**: JWT (HS256)
- **Pipelines**: Apache Airflow 2.8
- **Transformation**: dbt
- **Containerization**: Docker + Docker Compose

## Quick Start

```bash
# Start all services
docker-compose up -d

# Run API
uvicorn api.main:app --reload

# Run tests
pytest tests/
```

## Project Structure

```
├── api/                  # FastAPI routes
├── models/               # SQLAlchemy models with PostGIS
├── services/             # Business logic & ETL pipelines
├── workers/dags/         # Airflow DAGs
├── migrations/           # Database migrations
├── tests/                # Unit tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/token | Get JWT token |
| GET | /api/v1/deals | List deals |
| POST | /api/v1/deals | Create deal |
| GET | /api/v1/deals/{id} | Get deal |
| PATCH | /api/v1/deals/{id} | Update deal |
| POST | /api/v1/deals/{id}/analyze | Run AI analysis |

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: JWT signing key
- `OPENAI_API_KEY`: OpenAI API key