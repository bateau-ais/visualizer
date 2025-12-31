# NOVA Visualizer Backend

FastAPI backend for NOVA maritime anomaly detection visualization.

## Features

- ✅ REST API (vessels, anomalies, heatmap, stats)
- ✅ WebSocket real-time streaming
- ✅ Redis integration (positions, cache)
- ✅ NATS subscriber (`nova.fused`)
- ✅ External APIs (VesselFinder, MarineTraffic)
- ✅ Automatic heatmap generation

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root (app info) |
| GET | `/health` | Health check |
| GET | `/api/vessels` | List vessels |
| GET | `/api/vessels/{mmsi}` | Vessel details |
| GET | `/api/anomalies` | Recent anomalies |
| GET | `/api/anomalies/heatmap` | Heatmap data |
| GET | `/api/anomalies/stats` | Dashboard stats |
| WS | `/ws` | WebSocket stream |

## Architecture

```
backend/
├── main.py                 # FastAPI app
├── config.py               # Settings (Pydantic)
├── requirements.txt
├── api/
│   ├── vessels.py          # Vessel endpoints
│   ├── anomalies.py        # Anomaly endpoints
│   └── websocket.py        # WebSocket
├── models/
│   ├── vessel.py           # Pydantic models
│   └── anomaly.py
└── services/
    ├── redis_service.py    # Redis operations
    ├── nats_subscriber.py  # NATS listener
    └── vessel_api.py       # External APIs
```

## Dependencies

- Redis (positions, cache)
- NATS (message broker)
- VesselFinder API (photos, optional)

## Development

```bash
# API documentation (auto-generated)
http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```
