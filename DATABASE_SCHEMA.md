# Visualizer Database Schema

This document describes the persistence layer used by the NOVA Visualizer (and populated by the Fusioner). The system uses **Redis** as the primary data store for real-time state, caching, and limited history.

## Connection
The services connect to Redis using the following default configuration (overridable via environment variables):

- **Host**: `redis` (docker service name)
- **Port**: `6379`
- **Database**: `0`

## Data Model (Redis)

The data model deals with three main entities: Active Vessels, Trajectories, and Anomalies.

### Key Namespace

| Key Pattern | Type | TTL | Description | Writer |
|-------------|------|-----|-------------|--------|
| `vessel:position:{mmsi}` | String (JSON) | 30m | Latest AIS position and status for a vessel. | Fusioner |
| `vessels:active` | Hash | - | Map of active MMSIs to their last seen timestamp. Used for quick iteration. | Fusioner |
| `vessel:trajectory:{mmsi}` | ZSet | - | Ordered set of historical positions. Score = Timestamp. | Fusioner |
| `anomalies:recent` | ZSet | - | Global list of recent anomalies (last ~10k). Score = Timestamp. | Fusioner |
| `vessel:anomalies:{mmsi}` | ZSet | - | History of anomalies for a specific vessel. Score = Timestamp. | Fusioner |
| `vessel:clean_frames:{mmsi}` | String (Int) | 30m | Counter for clean frames used for hysteresis (recovery from anomaly). | Fusioner |
| `vessel:acknowledged:{mmsi}` | String | - | Timestamp when a vessel was acknowledged by a user. | Visualizer |
| `vessels:all_acknowledged` | Set | - | Set of all acknowledged MMSIs. | Visualizer |
| `heatmap:{params}` | String (JSON) | 1h | Cached heatmap data for specific query parameters. | Visualizer |

### JSON Structures

#### Vessel Position (`vessel:position:{mmsi}`)
```json
{
  "mmsi": 123456789,
  "name": "Vessel Name",
  "type": "Cargo",
  "lat": 45.123,
  "lon": -5.678,
  "heading": 180,
  "sog": 12.5,
  "cog": 182.0,
  "timestamp": "2024-01-21T12:00:00Z",
  "is_anomaly": true,
  "anomaly_score": 0.85,
  "status": 0
}
```

#### Trajectory Point (`vessel:trajectory:{mmsi}` member)
```json
{
  "lat": 45.123,
  "lon": -5.678,
  "timestamp": "2024-01-21T12:00:00Z"
}
```

#### Anomaly Event (`anomalies:recent` member)
```json
{
  "data_id": "uuid-string",
  "mmsi": 123456789,
  "timestamp": "2024-01-21T12:00:00Z",
  "score": 0.95,
  "reasons": ["Speed unrealistic", "Zone restricted"],
  "confidence": 0.8,
  "lat": 45.123,
  "lon": -5.678
}
```

## Schema Relationships

```mermaid
classDiagram
    class Redis {
        +String vessel:position:{mmsi}
        +Hash vessels:active
        +ZSet vessel:trajectory:{mmsi}
        +ZSet anomalies:recent
        +ZSet vessel:anomalies:{mmsi}
        +String vessel:clean_frames:{mmsi}
        +String vessel:acknowledged:{mmsi}
        +Set vessels:all_acknowledged
    }

    class VesselPosition {
        +int mmsi
        +float lat
        +float lon
        +string timestamp
        +bool is_anomaly
        +float anomaly_score
    }

    class TrajectoryPoint {
        +float lat
        +float lon
        +string timestamp
    }

    class AnomalyEvent {
        +string data_id
        +int mmsi
        +string[] reasons
        +float score
    }

    Redis --> VesselPosition : stores (TTL 30m)
    Redis --> TrajectoryPoint : stores in ZSet
    Redis --> AnomalyEvent : stores in ZSet
```

## Data Lifecycle

1.  **Ingestion**: `Fusioner` receives parsed AIS messages.
2.  **Processing**:
    - Updates `vessel:position:{mmsi}`.
    - Updates `vessels:active` hash.
    - Appends to `vessel:trajectory:{mmsi}` (retains last 24h/2000 points).
    - If anomaly detected:
        - Appends to `anomalies:recent` (global history).
        - Appends to `vessel:anomalies:{mmsi}` (vessel history).
        - Manages `vessel:clean_frames:{mmsi}` for hysteresis.
3.  **Visualization**:
    - `Visualizer` reads `vessels:active` -> `vessel:position:{mmsi}` to display live map.
    - Reads trajectory/anomaly ZSets for details.
    - Manages user acknowledgments (`vessel:acknowledged:{mmsi}`).
