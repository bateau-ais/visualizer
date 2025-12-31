# NOVA Visualizer - Cahier des Charges

**Version**: 1.0  
**Date**: 2025-12-31  
**Auteur**: Équipe NOVA

---

## 1. Vue d'Ensemble

### 1.1 Objectif

Le **NOVA Visualizer** est l'interface web de supervision et d'analyse pour le système de détection d'anomalies AIS. Il permet aux analystes maritimes de :

- Visualiser en temps réel les positions et trajectoires des navires
- Identifier rapidement les anomalies détectées par le système
- Analyser les zones à risque avec des heatmaps
- Consulter l'historique et les détails des navires
- Recevoir des notifications configurables sur les événements critiques

### 1.2 Utilisateurs Cibles

- **Analystes maritimes** - Surveillance quotidienne, investigation d'anomalies
- **Superviseurs** - Vue d'ensemble, tendances, métriques
- **Opérateurs SAR** - Réponse rapide aux incidents critiques
- **Administrateurs** - Configuration, gestion des utilisateurs

### 1.3 Périmètre

#### ✅ Inclus

- Interface web responsive (desktop prioritaire, tablet acceptable)
- Carte maritime interactive avec couches multiples
- Affichage en temps réel des positions AIS
- Visualisation des anomalies avec degrés de certitude
- Heatmaps configurables des zones à risque
- Fiches détaillées des navires (photos, historique, caractéristiques)
- Système de notifications push et email
- Dashboard avec métriques et statistiques
- Recherche et filtrage avancé
- Export de données (CSV, JSON, PDF)

#### ❌ Exclus (v1)

- Application mobile native (iOS/Android)
- Prédictions futures (LSTM, forecast)
- Corrélation multi-sources (radar, satellite)
- Gestion des opérations SAR (hors périmètre)
- Édition manuelle des données AIS

---

## 2. Fonctionnalités Principales

### 2.1 Carte Maritime Interactive

#### 2.1.1 Fond de Carte

**Spécifications** :
- **Projection** : Web Mercator (EPSG:3857)
- **Librairie** : Leaflet ou Mapbox GL JS
- **Tuiles de base** :
  - OpenStreetMap (fallback, gratuit)
  - OpenSeaMap (overlay maritime : routes, bouées, dangers)
  - NOAA/GEBCO bathymétrie (profondeurs, relief sous-marin)
- **Zoom** : Niveaux 2 (monde) à 18 (port)
- **Contrôles** : Zoom, pan, rotation, fullscreen, mesure de distance

**Couches disponibles** :
1. **Base nautique** - Carte maritime avec toponymie
2. **Bathymétrie** - Profondeurs et relief
3. **Zones maritimes** - ZEE, eaux territoriales, SCTM
4. **Routes maritimes** - Couloirs de navigation, TSS
5. **Météo** (optionnel) - Vent, vagues, courants

#### 2.1.2 Affichage des Navires

**Marqueurs navires** :
```javascript
{
  position: [lat, lon],
  mmsi: 123456789,
  vessel_name: "MAERSK ESSEX",
  icon: {
    type: "cargo",  // cargo, tanker, passenger, fishing, military, unknown
    size: "medium", // small (<50m), medium (50-200m), large (>200m)
    color: "#00FF00",  // Vert=normal, Orange=attention, Rouge=anomalie
    rotation: 245  // Orientation selon COG
  },
  tooltip: "MAERSK ESSEX (Cargo) - 12.5kt - 245°",
  popup: "Fiche détaillée avec photo"
}
```

**Icônes** :
- Forme selon type de navire (SVG customisés)
- Taille proportionnelle aux dimensions réelles
- Rotation selon cap (COG ou heading si disponible)
- Couleur selon statut :
  - 🟢 **Vert** : Normal
  - 🟠 **Orange** : Anomalie mineure (score 0.5-0.7)
  - 🔴 **Rouge** : Anomalie critique (score >0.7)
  - 🔵 **Bleu** : Sélectionné par l'utilisateur
  - ⚫ **Gris** : Donnée obsolète (>30min)

**Trajectoires** :
- Ligne pointillée pour l'historique (dernières 24h configurable)
- Gradient de couleur selon ancienneté (récent=opaque, ancien=transparent)
- Affichage on-demand (clic sur navire)
- Option "prédiction 1h" basée sur COG/SOG actuel

### 2.2 Heatmap des Anomalies

**Objectif** : Identifier visuellement les zones à forte concentration d'anomalies.

**Spécifications** :
- **Grille** : Configurable par l'utilisateur
  - **Haute résolution** : 0.01° (~1 km, 1 minute d'arc)
  - **Moyenne résolution** : 0.1° (~10 km, 6 minutes d'arc)
  - **Basse résolution** : 1° (~100 km, 1 degré)
- **Période** : Dernières 24h / 7j / 30j (sélectionnable)
- **Filtre** : Tous types / Speed / Heading / Spoofing
- **Rendu** : Gradient thermique
  - Bleu (0 anomalies) → Jaune (5-10) → Rouge (>20)
- **Interactivité** : Clic sur cellule → Liste des anomalies dans cette zone

**Calcul** :
```python
# Pseudo-code
grid_cell = {
  lat_min: 48.0,
  lat_max: 48.1,
  lon_min: -5.0,
  lon_max: -4.9,
  anomaly_count: 15,
  confidence_avg: 0.72,
  top_types: ["SPEED_SPIKE", "HEADING_CHANGE"]
}
```

### 2.3 Fiche Navire Détaillée

**Déclenchement** : Clic sur marqueur navire.

**Contenu** :

#### Section 1 : Identification
- **Photo du navire** (API externe : MarineTraffic, VesselFinder, ShipSpotting)
- **Nom** : MAERSK ESSEX
- **MMSI** : 123456789
- **IMO** : 9876543 (si disponible)
- **Type** : Container Ship (code AIS 70)
- **Pavillon** : 🇩🇰 Denmark (déduit du MMSI)
- **Indicatif** : OXYZ2
- **Dimensions** : 294m × 32m × 14m (LOA × Beam × Draft)

#### Section 2 : Position Actuelle
- **Coordonnées** : 48°14.123'N, 005°31.456'W
- **Vitesse** : 12.5 kt (SOG)
- **Cap** : 245° (COG) + compas miniature
- **Heading** : 247° (si différent de COG)
- **Statut** : Under way using engine (code 0)
- **Dernière mise à jour** : Il y a 2 minutes (timestamp précis)

#### Section 3 : Anomalies
- **Statut** : 🔴 **Anomalie détectée** (score 0.85)
- **Raisons** :
  - ⚠️ SPEED_SPIKE (conf. 90%)
  - ⚠️ SPOOFING_IMPOSSIBLE_SPEED (conf. 85%)
- **Détails** : Passage de 10kt à 25kt en 3 minutes (physiquement suspect)
- **Horodatage** : 2025-12-31 12:45:00 UTC

#### Section 4 : Historique
- **Graphique vitesse** (dernières 24h)
- **Graphique cap** (dernières 24h)
- **Liste des 10 dernières positions** (tableau)
- **Anomalies passées** : 3 détectées cette semaine

#### Section 5 : Actions
- 📌 **Épingler** (surveillance prioritaire)
- 📧 **Notifier par email** si nouvelles anomalies
- 📄 **Exporter rapport PDF**
- 🔗 **Voir sur MarineTraffic** (lien externe)

### 2.4 Système de Notifications

**Types de notifications** :

1. **En temps réel (WebSocket)** :
   - Toast notification dans l'interface
   - Son configurable (bip, alarme, custom)
   - Badge de compteur sur l'icône

2. **Email** :
   - Digest horaire/quotidien configurable
   - Alertes immédiates pour anomalies critiques (score >0.8)

3. **Webhook** (optionnel v2) :
   - POST vers URL externe pour intégration (Slack, Teams, SIEM)

**Configuration utilisateur** :
```yaml
notifications:
  real_time:
    enabled: true
    sound: "alert.mp3"
    min_score: 0.7  # Seuil déclenchement
    types: ["SPOOFING", "SPEED_SPIKE"]  # Filtrer par type
  
  email:
    enabled: true
    digest: "hourly"  # hourly, daily, never
    immediate_threshold: 0.8
    recipients: ["analyst@maritime.gov"]
```

### 2.5 Dashboard et Métriques

**Vue d'ensemble** (page d'accueil) :

#### Widgets temps réel :
- **Navires actifs** : 1,247 (mise à jour toutes les 10s)
- **Anomalies (24h)** : 89 détectées
- **Taux de détection** : 7.1% (↑ 0.3% vs hier)
- **Anomalies critiques** : 12 (score >0.8)

#### Graphiques :
1. **Timeline anomalies** : Barres par heure (dernières 24h)
2. **Répartition par type** : Pie chart (Speed 45%, Heading 30%, Spoofing 15%, Autres 10%)
3. **Top 10 zones** : Liste avec heatmap miniature
4. **Évolution détection** : Line chart sur 7 jours

#### Tableau "Anomalies récentes" :
| Horodatage | Navire | Type | Score | Actions |
|------------|--------|------|-------|---------|
| 12:45 | MAERSK ESSEX (123456789) | SPEED_SPIKE | 0.85 | 🔍 Voir |
| 12:42 | MSC FLORIDA (987654321) | HEADING_CHANGE | 0.72 | 🔍 Voir |

### 2.6 Recherche et Filtres

**Barre de recherche** :
- Par MMSI : 123456789
- Par nom : "MAERSK"
- Par IMO : 9876543
- Par zone géographique : "Manche" ou bbox

**Filtres avancés** (panneau latéral) :
- **Type de navire** : ☑ Cargo ☑ Tanker ☐ Passenger ☐ Fishing
- **Statut** : ☑ Normal ☑ Anomalie ☐ Critique uniquement
- **Vitesse** : 0-50 kt (slider)
- **Période** : Dernières 1h / 6h / 24h / 7j
- **Pavillon** : Sélection multiple
- **Zone** : Dessin manuel sur carte ou prédéfinies (Manche, Atlantique, etc.)

---

## 3. Architecture Technique

### 3.1 Stack Technologique

#### Backend
- **Framework** : **FastAPI** (Python 3.11+)
  - Raisons : Performance, WebSocket natif, OpenAPI auto, async
- **Base de données** : **Redis** (positions temps réel, cache)
- **Message broker** : **NATS** (abonnement à `nova.fused`)
- **Session store** : Redis (authentification)

#### Frontend
- **Framework** : **Vue.js 3** avec Composition API
  - Alternatives : React (plus verbose), Svelte (moins mature)
- **Carte** : **Leaflet** avec plugins
  - Alternatives : Mapbox GL JS (payant au-delà de seuil), OpenLayers (complexe)
- **UI Components** : **Vuetify 3** ou **PrimeVue**
- **Graphiques** : **Chart.js** ou **Apache ECharts**
- **État global** : **Pinia**
- **WebSocket** : **Socket.IO** (fallback HTTP long-polling)

#### Déploiement
- **Conteneurisation** : Docker + docker-compose
- **Reverse proxy** : Nginx (SSL, static files, caching)
- **Monitoring** : Prometheus + Grafana (métriques backend)

### 3.2 Architecture Backend

```
FastAPI Application
├── main.py                 # Point d'entrée, CORS, middleware
├── api/
│   ├── vessels.py          # GET /vessels, /vessels/{mmsi}
│   ├── anomalies.py        # GET /anomalies, /anomalies/heatmap
│   ├── notifications.py    # GET/POST /notifications/config
│   └── websocket.py        # WS /ws (streaming temps réel)
├── services/
│   ├── redis_service.py    # Accès Redis (positions, cache)
│   ├── nats_subscriber.py  # Écoute nova.fused, met à jour Redis
│   ├── vessel_api.py       # Appels API externes (photos, infos)
│   └── notification.py     # Gestion envoi emails, webhooks
├── models/
│   ├── vessel.py           # Pydantic: VesselPosition, VesselDetails
│   └── anomaly.py          # Pydantic: AnomalyEvent, HeatmapCell
└── config.py               # Settings (Redis URL, NATS URL, API keys)
```

### 3.3 API REST

#### Endpoints principaux

**GET /api/vessels**
```json
{
  "vessels": [
    {
      "mmsi": 123456789,
      "name": "MAERSK ESSEX",
      "lat": 48.2355,
      "lon": -5.5234,
      "sog": 12.5,
      "cog": 245,
      "heading": 247,
      "type": "cargo",
      "status": "underway",
      "last_update": "2025-12-31T12:45:00Z",
      "anomaly_score": 0.85,
      "is_anomaly": true
    }
  ],
  "total": 1247,
  "timestamp": "2025-12-31T12:50:00Z"
}
```

**GET /api/vessels/{mmsi}**
```json
{
  "mmsi": 123456789,
  "name": "MAERSK ESSEX",
  "imo": 9876543,
  "type": "cargo",
  "flag": "DK",
  "dimensions": {"length": 294, "beam": 32, "draft": 14},
  "current_position": {
    "lat": 48.2355,
    "lon": -5.5234,
    "sog": 12.5,
    "cog": 245,
    "timestamp": "2025-12-31T12:45:00Z"
  },
  "trajectory": [
    {"lat": 48.20, "lon": -5.50, "timestamp": "2025-12-31T12:00:00Z"},
    ...
  ],
  "anomalies": [
    {
      "timestamp": "2025-12-31T12:45:00Z",
      "score": 0.85,
      "reasons": ["SPEED_SPIKE", "SPOOFING_IMPOSSIBLE_SPEED"],
      "details": "Passage de 10kt à 25kt en 3min"
    }
  ],
  "photo_url": "https://cdn.marinetraffic.com/ships/123456789.jpg"
}
```

**GET /api/anomalies/heatmap**  
Paramètres : `?resolution=0.1&period=24h&type=all`
```json
{
  "cells": [
    {
      "lat_min": 48.0,
      "lat_max": 48.1,
      "lon_min": -5.0,
      "lon_max": -4.9,
      "count": 15,
      "avg_score": 0.72,
      "top_types": ["SPEED_SPIKE", "HEADING_CHANGE"]
    }
  ],
  "resolution": 0.1,
  "period": "24h"
}
```

**WS /ws**
```json
// Message envoyé par le serveur (événement temps réel)
{
  "type": "vessel_update",
  "mmsi": 123456789,
  "position": {"lat": 48.24, "lon": -5.52},
  "sog": 12.6,
  "timestamp": "2025-12-31T12:51:00Z"
}

{
  "type": "anomaly_detected",
  "mmsi": 987654321,
  "score": 0.88,
  "reasons": ["SPOOFING_TELEPORTATION_LIKELY"],
  "timestamp": "2025-12-31T12:51:30Z"
}
```

### 3.4 Intégration Redis

**Structure des clés** :

```
# Positions actuelles des navires (TTL 30 min)
vessel:position:{mmsi} → JSON {lat, lon, sog, cog, timestamp}

# Hash pour recherche rapide de tous les navires actifs
vessels:active → HASH {mmsi: last_timestamp}

# Trajectoires (ZSET avec score = timestamp)
vessel:trajectory:{mmsi} → ZSET 

# Anomalies récentes (Sorted Set)
anomalies:recent → ZSET (score = timestamp)

# Heatmap précalculée (cache 5 min)
heatmap:24h:0.1deg → JSON

# Config notifications par utilisateur
user:{user_id}:notifications → JSON
```

**Exemple requête** :
```python
# Récupérer tous les navires actifs
mmsis = redis.hkeys("vessels:active")
pipeline = redis.pipeline()
for mmsi in mmsis:
    pipeline.get(f"vessel:position:{mmsi}")
positions = pipeline.execute()
```

### 3.5 Intégration APIs Externes

#### Photos de Navires

**Option 1 : MarineTraffic API** (payant, ~€500/mois)
```python
GET https://api.marinetraffic.com/api/exportvessel/v:5/{API_KEY}/MMSI:123456789/protocol:jsono
Response: {"PHOTO": "https://photos.marinetraffic.com/..."}
```

**Option 2 : VesselFinder** (freemium, gratuit jusqu'à 1000 req/jour)
```python
GET https://www.vesselfinder.com/api/pub/vesselphoto/123456789
Response: {"url": "https://images.vesselfinder.com/..."}
```

**Option 3 : Scraping ShipSpotting** (gratuit, mais legal grey area)
- Chercher `mmsi:123456789` sur shipspotting.com
- Parser HTML pour extraire image

**Recommandation** : VesselFinder en v1 (gratuit), MarineTraffic si budget disponible.

#### Informations Navires

**IMO Lookup** : 
- API gratuite : https://www.imo.org/en/OurWork/IIIS/Pages/GISIS.aspx (scraping)
- API payante : IHS Markit (~€1000/an)

**Caractéristiques techniques** :
- Utiliser champ `vessel_type` du message AIS
- Base locale SQLite avec types AIS → noms lisibles

---

## 4. Interface Utilisateur (UI/UX)

### 4.1 Layout Principal

```
┌──────────────────────────────────────────────────────────────┐
│ NAVBAR: [NOVA Logo] [Dashboard] [Map] [Anomalies] [Search]  │
│                                      [🔔3] [User ▼] [⚙️]     │
├──────────────────────────────────────────────────────────────┤
│ SIDEBAR (300px)          │  MAIN CONTENT                     │
│ ┌─────────────────────┐  │  ┌──────────────────────────────┐│
│ │ Filtres             │  │  │                              ││
│ │ ☑ Cargo             │  │  │    CARTE MARITIME            ││
│ │ ☑ Tanker            │  │  │    (Leaflet)                 ││
│ │ ☐ Passenger         │  │  │                              ││
│ │                     │  │  │  🔵 Navire normal            ││
│ │ Statut:             │  │  │  🔴 Anomalie                 ││
│ │ ☑ Normal            │  │  │                              ││
│ │ ☑ Anomalie          │  │  │                              ││
│ │                     │  │  │                              ││
│ │ Vitesse: [0-50kt]   │  │  │                              ││
│ │ ═════╪══════        │  │  │                              ││
│ │     12              │  │  └──────────────────────────────┘│
│ │                     │  │                                   │
│ │ [Appliquer]         │  │  Layers: [Base] [Heatmap] [...]  │
│ └─────────────────────┘  │                                   │
│  ┌─────────────────────┐ │                                   │
│  │ Anomalies récentes  │ │                                   │
│  │ 12:45 MAERSK... 🔴 │ │                                   │
│  │ 12:42 MSC FLO... 🟠│ │                                   │
│  └─────────────────────┘ │                                   │
└──────────────────────────┴───────────────────────────────────┘
```

### 4.2 Page "Dashboard"

```
┌──────────────────────────────────────────────────────────────┐
│ Tableau de Bord - Vue d'Ensemble                             │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│ │ Navires │ │Anomalies│ │  Taux   │ │Critiques│             │
│ │  1,247  │ │   89    │ │  7.1%   │ │   12    │             │
│ │ actifs  │ │ (24h)   │ │(↑ 0.3%) │ │(score>8)│             │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
│                                                               │
│ ┌──────────────────────────┐ ┌──────────────────────────┐    │
│ │ Anomalies par heure      │ │ Répartition par type     │    │
│ │ ▄█▅▃▄▆▅█▅▃▄▆▅▃▄▆▅▃▄▆▅▃▄ │ │      Speed 45%           │    │
│ │                          │ │      Heading 30%         │    │
│ └──────────────────────────┘ │      Spoofing 15%        │    │
│                              │      Autres 10%           │    │
│                              └──────────────────────────┘    │
│                                                               │
│ Anomalies Récentes                                           │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Heure │ Navire       │ Type         │ Score │ Actions │   │
│ ├───────┼──────────────┼──────────────┼───────┼─────────┤   │
│ │12:45  │MAERSK ESSEX  │SPEED_SPIKE   │ 0.85  │🔍 Voir  │   │
│ │12:42  │MSC FLORIDA   │HEADING_CHANGE│ 0.72  │🔍 Voir  │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Popup Navire

Clic sur marqueur → Modal ou panneau latéral :

```
┌─────────────────────────────────────────────────┐
│ MAERSK ESSEX                          [X]       │
│ ┌─────────────────┐                             │
│ │  [Photo navire] │  MMSI: 123456789            │
│ │                 │  IMO: 9876543               │
│ └─────────────────┘  Type: Container Ship       │
│                      Pavillon: 🇩🇰 Denmark       │
│                                                  │
│ Position Actuelle                                │
│ ─────────────────                                │
│ 📍 48°14.123'N, 005°31.456'W                    │
│ 🧭 Cap: 245° (COG)                              │
│ ⚡ Vitesse: 12.5 kt                              │
│ 🕐 Mise à jour: Il y a 2 minutes                │
│                                                  │
│ ⚠️ Anomalie Détectée (Score: 0.85)              │
│ ─────────────────────────────────                │
│ • SPEED_SPIKE (conf. 90%)                       │
│ • SPOOFING_IMPOSSIBLE_SPEED (conf. 85%)         │
│                                                  │
│ [📊 Voir historique] [📌 Épingler] [📄 Export]  │
└─────────────────────────────────────────────────┘
```

### 4.4 Responsive Design

- **Desktop (>1280px)** : Layout complet avec sidebar
- **Tablet (768-1280px)** : Sidebar collapsible, carte pleine largeur
- **Mobile (<768px)** : Navbar hamburger, liste au lieu de carte (v2)

---

## 5. Spécifications Non Fonctionnelles

### 5.1 Performance

- **Latence WebSocket** : <500ms de bout-en-bout (NATS → Redis → WebSocket)
- **Chargement initial** : <3s (carte + positions des navires)
- **FPS carte** : 60 FPS avec 1000+ marqueurs (clustering si nécessaire)
- **API response time** : <200ms (P95)

### 5.2 Scalabilité

- **Navires simultanés** : Jusqu'à 10,000 (clustering au-delà)
- **Utilisateurs concurrents** : 50+ analystes
- **WebSocket** : 100 connexions simultanées

### 5.3 Sécurité

- **Authentification** : JWT tokens (expiration 24h)
- **Autorisation** : Rôles (admin, analyst, viewer)
- **HTTPS** : Obligatoire en production
- **CORS** : Whitelist des origins autorisées
- **Rate limiting** : 100 req/min par IP

### 5.4 Disponibilité

- **Uptime** : 99% (acceptable pour système de surveillance)
- **Backup Redis** : Snapshots quotidiens
- **Monitoring** : Prometheus + alertes si service down >5min

---

## 6. Roadmap et Priorisation

### Phase 1 - MVP (v1.0) - ~3 semaines
- ✅ Carte maritime avec positions en temps réel
- ✅ Affichage anomalies (couleurs marqueurs)
- ✅ Fiche navire basique (sans photos)
- ✅ Dashboard simplifié
- ✅ WebSocket streaming
- ✅ Export CSV

### Phase 2 - Améliorations (v1.1) - ~2 semaines
- ✅ Heatmap anomalies
- ✅ Recherche et filtres avancés
- ✅ Photos navires (API VesselFinder)
- ✅ Notifications email
- ✅ Historique graphiques (vitesse/cap)

### Phase 3 - Fonctionnalités avancées (v2.0) - ~4 semaines
- 🔮 Prédictions trajectoires (LSTM)
- 🔮 Notifications WebHook (Slack, Teams)
- 🔮 Export PDF rapports
- 🔮 Corrélation multi-sources (météo, AIS + radar)
- 🔮 App mobile (React Native)

---

## 7. Annexes

### 7.1 APIs Externes - Récapitulatif

| Service | Usage | Coût | Rate Limit |
|---------|-------|------|------------|
| **VesselFinder** | Photos navires | Gratuit (<1000/j) | 1000 req/jour |
| **MarineTraffic** | Photos + infos | ~€500/mois | Illimité |
| **OpenSeaMap** | Tuiles carte | Gratuit | Illimité |
| **GEBCO** | Bathymétrie | Gratuit | Illimité |
| **SendGrid** | Emails | Gratuit (<100/j) | 100 emails/jour |

### 7.2 Dépendances Python (Backend)

```txt
# requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
redis>=5.0.0
nats-py>=2.12.0
pydantic>=2.0.0
python-jose[cryptography]  # JWT
passlib[bcrypt]  # Hash passwords
httpx  # Appels API externes
jinja2  # Templates email
python-multipart  # Form data
```

### 7.3 Dépendances JavaScript (Frontend)

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "vuetify": "^3.5.0",
    "leaflet": "^1.9.4",
    "chart.js": "^4.4.0",
    "socket.io-client": "^4.6.0",
    "axios": "^1.6.0",
    "date-fns": "^3.0.0"
  }
}
```

---

**Fin du Cahier des Charges**
