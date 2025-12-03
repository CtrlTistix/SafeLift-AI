# SafeLift-AI - Industrial Forklift Safety Monitoring System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.108.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)](https://docs.docker.com/compose/)

**SafeLift-AI** is an enterprise-grade, real-time safety monitoring system designed to detect and prevent forklift-related accidents in industrial environments using IoT telemetry and AI-powered safety rules.

## 🎯 Features

### Safety Rules Engine
- ✅ **Impact Detection**: G-force threshold monitoring
- ✅ **Speed Violations**: Dangerous speed detection
- ✅ **Mast Tilt with Load**: Load stability monitoring
- ✅ **Excessive Braking**: Harsh braking detection
- ✅ **Proximity Alerts**: GPS-based proximity warnings
- ✅ **Operating Hours**: After-hours operation detection
- ✅ **Restricted Zones**: Geofenced area violations

### Backend (FastAPI)
- ✅ RESTful API with OpenAPI documentation
- ✅ JWT authentication with roles (admin/operator/viewer)
- ✅ PostgreSQL + SQLite support
- ✅ Real-time WebSocket for live updates
- ✅ Event bus architecture for decoupled components
- ✅ Structured logging with JSON format
- ✅ Comprehensive test suite (pytest)
- ✅ Docker deployment ready

### IoT Simulator
- ✅ Realistic forklift behavior simulation
- ✅ GPS position tracking within warehouse bounds
- ✅ 8 behavior scenarios (idle, driving, loading, violations)
- ✅ Physics-based acceleration calculations
- ✅ Configurable warehouse boundaries
- ✅ Multiple forklift simulation

### Frontend (In Progress)
- 🚧 React + TypeScript + Vite
- 🚧 TailwindCSS + ShadCN/UI components
- 🚧 Real-time dashboard
- 🚧 Forklift fleet map
- 🚧 Alert management

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### 1. Clone and Setup
```bash
git clone https://github.com/CtrlTistix/SafeLift-AI.git
cd SafeLift-AI

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Change SECRET_KEY in production!
```

### 2. Run with Docker Compose
```bash
# Start all services (PostgreSQL + Backend + Frontend + Simulator)
docker-compose up --build

# Or start without simulator
docker-compose up --build postgres backend frontend
```

**Services will be available at:**
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

### 3. Default Credentials
- Username: `admin`
- Password: `admin123`

**⚠️ Change these in production!**

---

## 📁 Project Structure

```
SafeLift-AI/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── core/              # Config, logging, security
│   │   ├── db/                # Models, repositories, sessions
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── services/          # Business logic & safety engine
│   │   ├── api/               # API routes & middlewares
│   │   └── websocket/         # WebSocket manager
│   ├── tests/                 # Pytest tests
│   ├── main.py               # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Production Docker image
├── edge/                      # Edge devices & IoT
│   └── simulator/            # Telemetry simulator
│       ├── forklift_simulator.py
│       ├── telemetry_generator.py
│       ├── config.py
│       └── Dockerfile
├── frontend/                  # React + TypeScript (WIP)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docs/                      # Documentation
│   ├── architecture.md
│   └── endpoints.md
├── docker-compose.yml         # Orchestration
└── .env.example              # Environment template
```

---

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run tests
pytest tests/ -v --cov=src
```

### Run Simulator Locally

```bash
cd edge/simulator

# Install dependencies
pip install -r requirements.txt

# Configure backend URL
export BACKEND_URL=http://localhost:8000

# Run simulator
python telemetry_generator.py
```

### Frontend Development (WIP)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## 📊 API Documentation

### Authentication
All API endpoints (except `/health` and `/docs`) require JWT authentication.

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Use token in requests:**
```bash
curl http://localhost:8000/api/events \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/docs` | Interactive API documentation |
| GET | `/health` | Health check |
| POST | `/api/auth/login` | User authentication |
| GET | `/api/events` | List safety events |
| POST | `/api/telemetry` | Ingest telemetry data |
| WS | `/ws/events` | Real-time event stream |

**Full API documentation:** http://localhost:8000/docs

---

## 🛡️ Safety Rules Configuration

Edit `backend/src/core/config.py` to customize thresholds:

```python
# Safety Rules Engine
IMPACT_THRESHOLD_G = 2.5              # G-force threshold
DANGEROUS_SPEED_KMH = 25.0            # Speed threshold
MAST_TILT_THRESHOLD_DEG = 15.0        # Mast tilt angle
BRAKING_FORCE_THRESHOLD_G = 1.5       # Braking force
PROXIMITY_DANGER_METERS = 3.0         # Proximity distance
WORK_START_HOUR = 6                   # Work start (6 AM)
WORK_END_HOUR = 22                    # Work end (10 PM)
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_safety_rules.py -v
```

### Test Coverage

The backend includes:
- ✅ Unit tests for safety rules engine
- ✅ Integration tests for API endpoints
- ✅ Authentication and authorization tests
- ✅ Database repository tests

---

## 🐳 Docker Deployment

### Production Build

```bash
# Build all services
docker-compose build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/safelift

# JWT Secret (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-characters

# CORS
CORS_ORIGINS=http://localhost:3000

# Simulator
NUM_FORKLIFTS=3
EVENT_INTERVAL=5
```

---

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Backend logs
docker-compose logs backend

# Simulator logs
docker-compose logs simulator

# Real-time logs
docker-compose logs -f
```

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value (min 32 characters)
- [ ] Change default admin password
- [ ] Use HTTPS/WSS in production
- [ ] Restrict CORS origins to your domain
- [ ] Enable database SSL connections
- [ ] Set up proper firewall rules
- [ ] Implement rate limiting
- [ ] Regular security audits

---

## 🎯 Roadmap

### Phase 1: Core Platform (✅ COMPLETE)
- [x] Backend API with FastAPI
- [x] Safety rules engine
- [x] IoT simulator
- [x] Docker deployment
- [x] Authentication & Authorization

### Phase 2: Frontend (🚧 IN PROGRESS)
- [ ] React + TypeScript dashboard
- [ ] Real-time event monitoring
- [ ] Forklift fleet map
- [ ] Alert management
- [ ] Analytics & reports

### Phase 3: Advanced Features
- [ ] Machine learning for predictive safety
- [ ] Mobile app (React Native)
- [ ] Email/SMS notifications
- [ ] Integration with Fleet IQ/XQ360
- [ ] Advanced analytics & heatmaps
- [ ] Multi-warehouse support

---

## 📞 Enterprise Integration

This system is designed to integrate with industrial telemetry platforms like:
- **Collective Intelligence Fleet IQ**
- **XQ360 Safety Platform**
- Custom ERP/WMS systems

Contact: [Your Contact Info]

---

## 📄 License

[Your License Here]

---

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

Built with modern enterprise-grade technologies:
- FastAPI - High-performance Python web framework
- PostgreSQL - Reliable SQL database
- SQLAlchemy - Python ORM
- Pydantic - Data validation
- React + TypeScript - Frontend framework
- Docker - Containerization

---

**SafeLift-AI** - Making Industrial WorkPlaces Safer Through Technology 🚜🛡️
