# SafeLift-AI API Documentation

## Base URLs

- **REST API**: `http://localhost:8000/api`
- **WebSocket**: `ws://localhost:8000/ws/events`

---

## REST API Endpoints

### 1. Health Check

Check if the backend service is running.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "SafeLift-AI Backend",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Service is healthy

---

### 2. Root Endpoint

Get API information.

**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "SafeLift-AI Backend API",
  "docs": "/docs",
  "health": "/health"
}
```

**Status Codes**:
- `200 OK`: Success

---

### 3. List Events

Retrieve a list of safety events with optional filtering.

**Endpoint**: `GET /api/events`

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of events to skip (pagination) |
| limit | integer | No | 100 | Maximum number of events to return |
| severity | integer | No | - | Filter by severity (1-5) |
| type | string | No | - | Filter by event type |

**Example Request**:
```bash
GET /api/events?severity=5&limit=10
```

**Response**:
```json
[
  {
    "id": 123,
    "timestamp": "2025-12-03T15:30:45.123456",
    "type": "person_near_forklift",
    "severity": 5,
    "source": "camera_1",
    "metadata": {
      "distance_pixels": 85.5,
      "person_confidence": 0.95,
      "forklift_confidence": 0.89,
      "person_bbox": {
        "x1": 120.0,
        "y1": 200.0,
        "x2": 180.0,
        "y2": 350.0
      },
      "forklift_bbox": {
        "x1": 300.0,
        "y1": 180.0,
        "x2": 450.0,
        "y2": 400.0
      },
      "frame_number": 1234
    }
  }
]
```

**Status Codes**:
- `200 OK`: Success
- `500 Internal Server Error`: Database error

---

### 4. Create Event

Create a new safety event. This automatically broadcasts the event to all connected WebSocket clients.

**Endpoint**: `POST /api/events`

**Request Body**:
```json
{
  "type": "person_near_forklift",
  "severity": 4,
  "source": "camera_1",
  "metadata": {
    "distance_pixels": 150.0,
    "person_confidence": 0.92,
    "forklift_confidence": 0.88,
    "additional_info": "Worker in exclusion zone"
  }
}
```

**Field Descriptions**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| type | string | Yes | - | Event type classification |
| severity | integer | Yes | 1-5 | Risk level (1=low, 5=critical) |
| source | string | Yes | - | Camera or sensor identifier |
| metadata | object | No | - | Additional event data (flexible) |

**Response**:
```json
{
  "id": 124,
  "timestamp": "2025-12-03T15:31:20.456789",
  "type": "person_near_forklift",
  "severity": 4,
  "source": "camera_1",
  "metadata": {
    "distance_pixels": 150.0,
    "person_confidence": 0.92,
    "forklift_confidence": 0.88,
    "additional_info": "Worker in exclusion zone"
  }
}
```

**Status Codes**:
- `201 Created`: Event created successfully
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Database error

**Validation Rules**:
- Severity must be between 1 and 5
- All required fields must be present
- Metadata can be an empty object or contain any valid JSON

---

### 5. Get Event by ID

Retrieve a specific event by its ID.

**Endpoint**: `GET /api/events/{event_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| event_id | integer | Unique event identifier |

**Example Request**:
```bash
GET /api/events/123
```

**Response**:
```json
{
  "id": 123,
  "timestamp": "2025-12-03T15:30:45.123456",
  "type": "person_near_forklift",
  "severity": 5,
  "source": "camera_1",
  "metadata": {
    "distance_pixels": 85.5,
    "person_confidence": 0.95
  }
}
```

**Status Codes**:
- `200 OK`: Success
- `404 Not Found`: Event does not exist
- `500 Internal Server Error`: Database error

---

## WebSocket API

### Event Stream

Connect to receive real-time safety event updates.

**Endpoint**: `WS /ws/events`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onopen = () => {
  console.log('Connected to event stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New event:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from event stream');
};
```

**Messages from Server**:

**Event Broadcast**:
When a new event is created via `POST /api/events`, it's automatically broadcast to all connected clients:

```json
{
  "id": 125,
  "timestamp": "2025-12-03T15:32:10.789012",
  "type": "person_near_forklift",
  "severity": 3,
  "source": "camera_2",
  "metadata": {
    "distance_pixels": 180.0
  }
}
```

**Messages to Server**:

**Ping Message**:
Send a ping to keep the connection alive:
```javascript
ws.send('ping');
```

**Pong Response**:
Server responds with:
```
pong
```

**Best Practices**:
1. Implement auto-reconnect logic (see dashboard `ws.js` for example)
2. Send periodic pings (every 30 seconds recommended)
3. Handle connection errors gracefully
4. Process events asynchronously to avoid blocking

---

## Event Types

### Common Event Types

| Type | Description | Typical Severity |
|------|-------------|------------------|
| person_near_forklift | Person detected too close to forklift | 3-5 |
| collision_risk | Potential collision detected | 4-5 |
| speed_violation | Forklift exceeding speed limit | 2-4 |
| restricted_area | Entry into restricted zone | 3-5 |
| improper_loading | Unsafe loading detected | 2-4 |
| no_ppe | Worker without safety equipment | 3-4 |

### Severity Levels

| Level | Label | Description | Use Case |
|-------|-------|-------------|----------|
| 1 | Low | Minor observation | Informational alerts |
| 2 | Minor | Small concern | Non-urgent issues |
| 3 | Moderate | Attention needed | Potential safety risks |
| 4 | High | Urgent attention required | Immediate safety concerns |
| 5 | Critical | Emergency response needed | Imminent danger |

---

## Error Responses

All endpoints may return the following error responses:

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "severity"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### Not Found (404)
```json
{
  "detail": "Event not found"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider:
- Implementing rate limiting per source/camera
- Setting maximum events per minute
- Using Redis for distributed rate limiting

---

## Authentication

The current implementation does not include authentication. For production:

**Recommended Approach**:
1. Implement JWT-based authentication
2. Add API keys for vision module endpoints
3. Use HTTPS/WSS in production
4. Implement role-based access control (RBAC)

**Example with JWT** (future enhancement):
```bash
POST /api/events
Authorization: Bearer <jwt_token>
```

---

## CORS Configuration

CORS is configured to allow all origins in development:
```python
allow_origins=["*"]
```

For production, restrict to specific origins:
```python
allow_origins=["https://dashboard.safelift-ai.com"]
```

---

## API Versioning

Current version: `v1.0.0`

Future versions will use URL-based versioning:
- `/api/v1/events`
- `/api/v2/events`

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints and schemas
- Test API calls directly in the browser
- Download OpenAPI specification

---

## Example Usage

### Python (requests)

```python
import requests

# Create an event
event_data = {
    "type": "person_near_forklift",
    "severity": 4,
    "source": "camera_1",
    "metadata": {"distance": 120.0}
}

response = requests.post(
    "http://localhost:8000/api/events",
    json=event_data
)

print(response.json())
```

### JavaScript (fetch)

```javascript
// Create an event
const eventData = {
  type: "person_near_forklift",
  severity: 4,
  source: "camera_1",
  metadata: { distance: 120.0 }
};

fetch('http://localhost:8000/api/events', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(eventData)
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### curl

```bash
# List events
curl http://localhost:8000/api/events

# Create event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "person_near_forklift",
    "severity": 4,
    "source": "camera_1",
    "metadata": {"distance": 120.0}
  }'

# Get specific event
curl http://localhost:8000/api/events/123
```

---

## Troubleshooting

### WebSocket Connection Issues

**Problem**: WebSocket disconnects frequently

**Solutions**:
- Implement ping/pong heartbeat (already included)
- Check firewall settings
- Verify proxy configuration for WebSocket support
- Use WSS (WebSocket Secure) in production

### Database Connection Errors

**Problem**: "could not connect to server"

**Solutions**:
- Verify PostgreSQL is running
- Check DATABASE_URL environment variable
- Ensure database exists
- Verify network connectivity

### CORS Errors

**Problem**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions**:
- Verify CORS middleware is configured
- Check allowed origins list
- Use proper protocol (http/https)
- Clear browser cache

---

## Support

For issues or questions:
- Check the interactive documentation at `/docs`
- Review the architecture documentation
- Examine server logs for errors
- Test with curl or Postman before using in application
