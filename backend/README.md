# SafeLift-AI Backend

FastAPI backend for real-time forklift safety monitoring system.

## Features

- **RESTful API**: CRUD operations for safety events
- **WebSocket Support**: Real-time event broadcasting to connected clients
- **PostgreSQL Database**: Persistent storage with SQLAlchemy ORM
- **CORS Enabled**: Cross-origin support for frontend integration

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/safelift_db"
```

Default credentials (development):
- Username: `safelift`
- Password: `safelift`
- Database: `safelift_db`

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check service status

### Events
- `GET /api/events` - List all events (with optional filters)
- `POST /api/events` - Create new event
- `GET /api/events/{id}` - Get specific event

### WebSocket
- `WS /ws/events` - Real-time event stream

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Event Schema

```json
{
  "type": "person_near_forklift",
  "severity": 4,
  "source": "camera_1",
  "metadata": {
    "distance": 2.5,
    "confidence": 0.95
  }
}
```

### Severity Levels
- 1: Low risk
- 2: Minor concern
- 3: Moderate risk
- 4: High risk
- 5: Critical danger

## Development

### Database Migrations

The application automatically creates tables on startup. For production, consider using Alembic for migrations.

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string

## Testing

```bash
pytest
```
