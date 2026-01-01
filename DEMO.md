# NOVA Visualizer - Quick Start (Demo Mode)

## Démarrage Rapide - Mode Démo

Le mode démo permet de lancer l'application **sans Redis ni NATS** avec des données fictives réalistes.

### Lancement du Mode Démo

#### Backend
```bash
cd visualizer/backend

# Installer les dépendances
pip install -r requirements.txt

# Utiliser la configuration démo
cp .env.demo .env

# Lancer le serveur
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd visualizer/frontend

# Installer les dépendances
npm install

# Lancer le serveur de dev
npm run dev
```

### Accès

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Données de Démo

Le mode démo génère automatiquement :
- **50 navires fictifs** répartis dans 5 zones maritimes
- **~10 anomalies** (20% des navires)
- **Mise à jour en temps réel** toutes les 5 secondes
- **Heatmap dynamique** basée sur les anomalies

### Zones Maritimes Simulées

- Manche (English Channel)
- Mer du Nord
- Méditerranée
- Atlantique
- Baltique

### Types d'Anomalies Simulées

- `SPEED_SPIKE` - Pics de vitesse suspects
- `HEADING_CHANGE` - Changements de cap brusques
- `SPOOFING_IMPOSSIBLE_SPEED` - Vitesse physiquement impossible
- `SPOOFING_TELEPORTATION_LIKELY` - Téléportation probable
- `VELOCITY_VARIANCE_HIGH` - Variance de vitesse élevée

### Passage en Mode Production

Pour basculer en mode production avec Redis/NATS :

```bash
# Backend
cp .env.example .env
# Éditer .env et mettre DEMO_MODE=False
# Configurer REDIS_HOST, NATS_URL, etc.
```

### Avantages du Mode Démo

✅ **Aucune infrastructure requise** (pas de Redis, NATS)  
✅ **Démarrage instantané** (~5 secondes)  
✅ **Données réalistes** pour démonstration  
✅ **Idéal pour développement frontend**  
✅ **Parfait pour démos et présentations**

### Limitations du Mode Démo

❌ Pas de persistance des données  
❌ Pas d'intégration NATS réelle  
❌ Pas de photos de navires (placeholders)  
❌ Trajectoires simplifiées

---

## Mode Production (Avec Infrastructure)

Voir [`README.md`](README.md) pour le mode production complet avec Redis et NATS.
