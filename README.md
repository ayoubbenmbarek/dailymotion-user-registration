# Dailymotion User Registration API

A user registration API with email verification built with FastAPI, PostgreSQL, and Docker.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DOCKER COMPOSE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐         ┌─────────────────┐         ┌─────────────────┐   │
│  │   Client    │         │   FastAPI App   │         │   PostgreSQL    │   │
│  │  (curl/UI)  │────────▶│   (port 8001)   │────────▶│   (port 5432)   │   │
│  └─────────────┘         └────────┬────────┘         └─────────────────┘   │
│                                   │                                         │
│                                   │ SMTP                                    │
│                                   ▼                                         │
│                          ┌─────────────────┐                                │
│                          │     MailHog     │                                │
│                          │  SMTP: 1025     │                                │
│                          │  Web UI: 8025   │                                │
│                          └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Running the Application

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

The services will be available at:
- **API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **MailHog Web UI**: http://localhost:8025

## API Endpoints

### Health Check

```bash
curl http://localhost:8001/health
```

### Register a New User

```bash
curl -X POST http://localhost:8001/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "message": "Registration successful. Please check your email for the activation code."
}
```

### View Activation Code

1. Open MailHog UI: http://localhost:8025
2. Find the email sent to your registered address
3. Copy the 4-digit activation code

### Activate Account

```bash
curl -X POST http://localhost:8001/users/activate \
  -u "test@example.com:SecurePass123" \
  -H "Content-Type: application/json" \
  -d '{"code": "1234"}'
```

**Response:**
```json
{
  "message": "Account activated successfully"
}
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Testing

### Run Tests

```bash
# Run tests inside Docker
docker-compose exec api pytest -v

# Or run locally with pytest (requires dependencies installed)
pytest -v
```

## Project Structure

```
DailyMotionUserRegistration/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings via Pydantic BaseSettings
│   ├── database.py          # asyncpg connection pool
│   ├── dependencies.py      # FastAPI dependency injection
│   ├── exceptions.py        # Custom HTTP exceptions
│   ├── models/
│   │   └── user.py          # Pydantic models
│   ├── repositories/
│   │   └── user_repository.py  # Data access layer (raw SQL)
│   ├── services/
│   │   ├── user_service.py     # Business logic
│   │   └── email_service.py    # Email abstraction
│   └── routers/
│       └── users.py         # API endpoints
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_registration.py
│   └── test_activation.py
├── migrations/
│   └── 001_create_users_table.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Technical Decisions

### Database: PostgreSQL with asyncpg

- Native async support for high performance
- Raw SQL queries (no ORM) via asyncpg
- UUID primary keys for better security
- Connection pooling for efficiency

### Password Security

- bcrypt hashing via passlib
- Minimum 8 character requirement
- Passwords never stored in plain text

### Email Service

- Abstract interface pattern for easy testing/swapping
- MailHog for local development (SMTP capture)
- Emails viewable at http://localhost:8025

### Activation Code

- 4-digit cryptographically secure code
- 1-minute expiration
- One-time use (cleared after activation)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://postgres:postgres@db:5432/dailymotion | PostgreSQL connection string |
| SMTP_HOST | mailhog | SMTP server hostname |
| SMTP_PORT | 1025 | SMTP server port |
| DEBUG | true | Enable debug mode |

## Stopping the Application

```bash
docker-compose down

# To also remove volumes (database data)
docker-compose down -v
```
