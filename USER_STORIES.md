# NOVA Visualizer - User Stories & Wireframes

## User Stories

### Epic 1 : Surveillance Temps Réel

#### US-001 : Voir les navires en temps réel
**En tant qu'** analyste maritime  
**Je veux** voir tous les navires actifs sur une carte en temps réel  
**Afin de** surveiller le trafic maritime dans ma zone de responsabilité

**Critères d'acceptation** :
- [ ] La carte affiche tous les navires avec positions <30min
- [ ] Les marqueurs sont colorés selon le statut (vert/orange/rouge)
- [ ] La carte se met à jour automatiquement (WebSocket)
- [ ] Je peux zoomer/dézoomer et naviguer sur la carte
- [ ] Les icônes sont orientées selon le cap du navire

---

#### US-002 : Identifier rapidement les anomalies
**En tant qu'** analyste maritime  
**Je veux** distinguer visuellement les navires avec anomalies  
**Afin de** prioriser mon investigation

**Critères d'acceptation** :
- [ ] Les navires avec anomalies sont en rouge/orange
- [ ] Un badge indique le score de confiance
- [ ] Le tooltip indique le type d'anomalie
- [ ] Je peux filtrer pour n'afficher que les anomalies

---

#### US-003 : Consulter les détails d'un navire
**En tant qu'** analyste maritime  
**Je veux** voir les informations détaillées d'un navire  
**Afin de** évaluer la criticité d'une anomalie

**Critères d'acceptation** :
- [ ] Clic sur marqueur → popup avec détails
- [ ] Affichage : MMSI, nom, type, position, vitesse, cap
- [ ] Section "Anomalies" si applicable
- [ ] Photo du navire si disponible (API externe)
- [ ] Lien vers historique complet

---

### Epic 2 : Analyse des Zones à Risque

#### US-004 : Visualiser les zones à forte concentration d'anomalies
**En tant qu'** superviseur  
**Je veux** une heatmap des anomalies  
**Afin d'** identifier les zones maritimes problématiques

**Critères d'acceptation** :
- [ ] Toggle "Heatmap" active une couche de chaleur
- [ ] Gradient thermique (bleu → jaune → rouge)
- [ ] Configuration de la résolution (1km, 10km, 100km)
- [ ] Filtrage par période (24h, 7j, 30j)
- [ ] Clic sur cellule → liste des anomalies dans cette zone

---

#### US-005 : Exporter les données d'anomalies
**En tant qu'** analyste  
**Je veux** exporter les anomalies d'une zone  
**Afin de** les partager avec d'autres services

**Critères d'acceptation** :
- [ ] Bouton "Export CSV" télécharge un fichier
- [ ] Colonnes : timestamp, MMSI, nom, type, score, raisons
- [ ] Option d'export PDF pour rapport formel
- [ ] Possibilité de filtrer avant export

---

### Epic 3 : Notifications et Alertes

#### US-006 : Recevoir des alertes temps réel
**En tant qu'** opérateur SAR  
**Je veux** être notifié immédiatement des anomalies critiques  
**Afin de** réagir rapidement

**Critères d'acceptation** :
- [ ] Toast notification pour anomalie score >0.7
- [ ] Son d'alerte configurable
- [ ] Badge de compteur sur icône cloche
- [ ] Clic sur notification → navire concerné sur carte

---

#### US-007 : Configurer mes préférences de notifications
**En tant qu'** analyste  
**Je veux** personnaliser mes notifications  
**Afin de** ne recevoir que les alertes pertinentes

**Critères d'acceptation** :
- [ ] Page "Paramètres → Notifications"
- [ ] Seuil de score ajustable (slider)
- [ ] Filtrage par type d'anomalie (checkboxes)
- [ ] Option email digest (horaire/quotidien)
- [ ] Sauvegarde des préférences par utilisateur

---

### Epic 4 : Recherche et Historique

#### US-008 : Rechercher un navire spécifique
**En tant qu'** analyste  
**Je veux** trouver rapidement un navire par MMSI ou nom  
**Afin de** vérifier son statut actuel

**Critères d'acceptation** :
- [ ] Barre de recherche en haut de page
- [ ] Autocomplétion sur nom de navire
- [ ] Recherche par MMSI (9 chiffres)
- [ ] Résultat → centrage carte + popup ouvert

---

#### US-009 : Consulter l'historique d'un navire
**En tant qu'** analyste  
**Je veux** voir les positions passées d'un navire  
**Afin de** reconstituer sa trajectoire

**Critères d'acceptation** :
- [ ] Bouton "Historique" dans popup navire
- [ ] Graphique vitesse sur 24h
- [ ] Graphique cap sur 24h
- [ ] Tracé de la trajectoire sur carte
- [ ] Liste des anomalies passées (7 derniers jours)

---

### Epic 5 : Dashboard et Métriques

#### US-010 : Vue d'ensemble du système
**En tant que** superviseur  
**Je veux** un dashboard avec KPIs  
**Afin de** suivre la performance du système

**Critères d'acceptation** :
- [ ] Widget "Navires actifs" (nombre total)
- [ ] Widget "Anomalies 24h" (nombre + taux)
- [ ] Graphique timeline (anomalies par heure)
- [ ] Pie chart répartition par type
- [ ] Tableau "Anomalies récentes" (10 dernières)

---

## Wireframes ASCII

### Wireframe 1 : Page Principale (Carte)

```
╔════════════════════════════════════════════════════════════════════════════╗
║ NOVA Visualizer                    🔍 Search   🔔(3)  👤 User ▼   ⚙️      ║
╠════════════════════════════════════════════════════════════════════════════╣
║                    │                                                        ║
║  FILTRES           │   ┌────────────────────────────────────────────────┐  ║
║  ───────           │   │                                                │  ║
║  Type de Navire    │   │            CARTE MARITIME                      │  ║
║  ☑ Cargo           │   │            (Leaflet Map)                       │  ║
║  ☑ Tanker          │   │                                                │  ║
║  ☐ Passenger       │   │    🟢 Normal vessel                            │  ║
║  ☐ Fishing         │   │    🔴 Anomaly detected                         │  ║
║                    │   │                                                │  ║
║  Statut            │   │          48°N                                  │  ║
║  ☑ Normal          │   │            │                                   │  ║
║  ☑ Anomalie        │   │         🟢─┼─🔴                                │  ║
║  ☐ Critique        │   │            │   🟢                              │  ║
║                    │   │ ───────────┼───────────                        │  ║
║  Vitesse           │   │ 5°W        0°        5°E                       │  ║
║  ╞═══════╪═══╡     │   │                                                │  ║
║  0      12     50  │   │                                                │  ║
║                    │   └────────────────────────────────────────────────┘  ║
║  [Appliquer]       │   Layers: [🌍 Base] [🔥 Heatmap] [📍 Zones]          ║
║  [Réinitialiser]   │                                                        ║
║                    │                                                        ║
║  ANOMALIES         │                                                        ║
║  ───────────       │                                                        ║
║  🔴 12:45          │                                                        ║
║  MAERSK ESSEX      │                                                        ║
║  Score: 0.85       │                                                        ║
║                    │                                                        ║
║  🟠 12:42          │                                                        ║
║  MSC FLORIDA       │                                                        ║
║  Score: 0.72       │                                                        ║
║                    │                                                        ║
╚════════════════════╧════════════════════════════════════════════════════════╝
```

### Wireframe 2 : Popup Navire

```
┌─────────────────────────────────────────────────────────┐
│  MAERSK ESSEX                                 [✕]      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  MMSI: 123456789                      │
│  │             │  IMO: 9876543                          │
│  │   [PHOTO]   │  Type: Container Ship                  │
│  │             │  Pavillon: 🇩🇰 Denmark                  │
│  └─────────────┘  Dimensions: 294m × 32m               │
│                                                          │
│  POSITION ACTUELLE                                       │
│  ──────────────────                                      │
│  📍 48°14.123'N, 005°31.456'W                           │
│  🧭 Cap: 245° (COG) | Heading: 247°                     │
│           N                                              │
│          ╱│╲                                             │
│         ╱ │ ╲                                            │
│        ╱  │  ╲                                           │
│       ╱   │   ╲                                          │
│  W ───────┼─────── E      ← 245°                        │
│           │                                              │
│           S                                              │
│                                                          │
│  ⚡ Vitesse: 12.5 kt (SOG)                               │
│  🕐 Dernière mise à jour: Il y a 2 minutes              │
│                                                          │
│  ⚠️  ANOMALIE DÉTECTÉE                                   │
│  ───────────────────                                     │
│  Score de confiance: 0.85 (Critique)                    │
│  ┌────────────────────────────────────────────────┐     │
│  │ • SPEED_SPIKE (conf. 90%)                      │     │
│  │   Passage de 10kt à 25kt en 3 minutes          │     │
│  │                                                 │     │
│  │ • SPOOFING_IMPOSSIBLE_SPEED (conf. 85%)        │     │
│  │   Vitesse de 25kt impossible pour cargo        │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  [📊 Voir Historique]  [📌 Épingler]  [📄 Export PDF]   │
│  [🔗 MarineTraffic]    [✉️ Notifier par email]          │
└─────────────────────────────────────────────────────────┘
```

### Wireframe 3 : Dashboard

```
╔════════════════════════════════════════════════════════════════════════════╗
║ NOVA Dashboard                                     👤 User ▼   ⚙️          ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  VUE D'ENSEMBLE                                                             ║
║  ───────────────                                                            ║
║                                                                             ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   ║
║  │ Navires      │  │ Anomalies    │  │ Taux         │  │ Critiques    │   ║
║  │ Actifs       │  │ Détectées    │  │ Détection    │  │ (Score >0.8) │   ║
║  │              │  │              │  │              │  │              │   ║
║  │   1,247      │  │     89       │  │   7.1%       │  │     12       │   ║
║  │              │  │  (24h)       │  │  (↑ 0.3%)    │  │              │   ║
║  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   ║
║                                                                             ║
║  ┌────────────────────────────────────┐  ┌──────────────────────────────┐  ║
║  │ ANOMALIES PAR HEURE (24h)          │  │ RÉPARTITION PAR TYPE         │  ║
║  │                                    │  │                              │  ║
║  │  █                                 │  │   Speed        ████████ 45% │  ║
║  │  █     █                           │  │   Heading      ██████   30% │  ║
║  │  █  █  █  █     █                  │  │   Spoofing     ███      15% │  ║
║  │  █  █  █  █  █  █  █               │  │   Autres       ██       10% │  ║
║  │  █  █  █  █  █  █  █  █            │  │                              │  ║
║  │ ─────────────────────────────────  │  └──────────────────────────────┘  ║
║  │ 00 04 08 12 16 20         Heure    │                                    ║
║  └────────────────────────────────────┘                                    ║
║                                                                             ║
║  ANOMALIES RÉCENTES                                                         ║
║  ────────────────────                                                       ║
║  ┌──────┬─────────────────┬──────────────────┬───────┬─────────────────┐   ║
║  │ Heure│ Navire (MMSI)   │ Type             │ Score │ Actions         │   ║
║  ├──────┼─────────────────┼──────────────────┼───────┼─────────────────┤   ║
║  │12:45 │MAERSK ESSEX     │SPEED_SPIKE       │ 🔴0.85│[🔍 Détails]     │   ║
║  │      │(123456789)      │SPOOFING_SPEED    │       │[📌 Épingler]    │   ║
║  ├──────┼─────────────────┼──────────────────┼───────┼─────────────────┤   ║
║  │12:42 │MSC FLORIDA      │HEADING_CHANGE    │ 🟠0.72│[🔍 Détails]     │   ║
║  │      │(987654321)      │                  │       │[📌 Épingler]    │   ║
║  ├──────┼─────────────────┼──────────────────┼───────┼─────────────────┤   ║
║  │12:38 │CMA CGM PARIS    │VELOCITY_VARIANCE │ 🟠0.68│[🔍 Détails]     │   ║
║  │      │(111222333)      │                  │       │[✓ Traité]       │   ║
║  └──────┴─────────────────┴──────────────────┴───────┴─────────────────┘   ║
║                                                                             ║
║  [⬇️ Exporter CSV]  [⬇️ Exporter PDF]  [🔄 Rafraîchir]                     ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### Wireframe 4 : Heatmap View

```
╔════════════════════════════════════════════════════════════════════════════╗
║ NOVA - Heatmap des Anomalies                                               ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Configuration Heatmap                                                      ║
║  ──────────────────────                                                     ║
║  Résolution: ● 1 km  ○ 10 km  ○ 100 km                                     ║
║  Période:    ● 24h   ○ 7 jours  ○ 30 jours                                 ║
║  Type:       ● Tous  ○ Speed  ○ Heading  ○ Spoofing                        ║
║                                                                             ║
║  ┌──────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                       │  ║
║  │        🟦 Zone calme (0-2 anomalies)                                  │  ║
║  │        🟨 Zone surveillée (3-10 anomalies)                            │  ║
║  │        🟥 Zone critique (>10 anomalies)                               │  ║
║  │                                                                       │  ║
║  │    50°N ┌────────────────────────────────┐                           │  ║
║  │         │       🟦  🟦  🟦  🟦  🟦  🟦   │                           │  ║
║  │         │       🟦  🟨  🟨  🟦  🟦  🟦   │                           │  ║
║  │    48°N │       🟦  🟨  🟥  🟨  🟦  🟦   │  ← Manche (zone dense)    │  ║
║  │         │       🟦  🟨  🟨  🟦  🟦  🟦   │                           │  ║
║  │         │       🟦  🟦  🟦  🟦  🟦  🟦   │                           │  ║
║  │    46°N └────────────────────────────────┘                           │  ║
║  │           5°W    0°     5°E                                           │  ║
║  │                                                                       │  ║
║  │  Clic sur une cellule pour voir les détails                          │  ║
║  └──────────────────────────────────────────────────────────────────────┘  ║
║                                                                             ║
║  DÉTAILS CELLULE SÉLECTIONNÉE (48.0°N - 48.1°N, -1.0°W - -0.9°W)          ║
║  ────────────────────────────────────────────────────────────────────       ║
║  Anomalies: 23                                                              ║
║  Confiance moyenne: 0.68                                                    ║
║  Types principaux: SPEED_SPIKE (12), HEADING_CHANGE (8), Autres (3)        ║
║                                                                             ║
║  [📊 Voir liste complète]  [⬇️ Exporter zone]                              ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### Wireframe 5 : Historique Navire

```
┌──────────────────────────────────────────────────────────────────┐
│  Historique - MAERSK ESSEX (123456789)             [✕]          │
├──────────────────────────────────────────────────────────────────┤
│  Période: [24 heures ▼]    Du: [31/12 00:00] Au: [31/12 23:59] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  VITESSE (SOG) - Dernières 24h                                   │
│  ──────────────────────────                                      │
│  25kt│                 ╱╲                                        │
│  20kt│                ╱  ╲                                       │
│  15kt│               ╱    ╲                                      │
│  10kt│──────────────╱      ╲─────────                           │
│   5kt│                                                           │
│   0kt└────────────────────────────────────────────────────       │
│      00h  04h  08h  12h  16h  20h  24h                           │
│                         ↑                                        │
│                    Anomalie détectée (12:45)                     │
│                                                                   │
│  CAP (COG) - Dernières 24h                                       │
│  ──────────────────────────                                      │
│  360°│        ╱────╲                                             │
│  270°│       ╱      ╲                                            │
│  180°│──────╱        ╲────────                                   │
│   90°│                                                            │
│    0°└────────────────────────────────────────────────────       │
│      00h  04h  08h  12h  16h  20h  24h                           │
│                                                                   │
│  TRAJECTOIRE SUR CARTE                                           │
│  ──────────────────────                                          │
│  ┌────────────────────────────────────┐                          │
│  │      Plymouth                      │                          │
│  │         │                           │                          │
│  │         ●───●───●  (trace 24h)     │                          │
│  │                ╲                    │                          │
│  │                 ●───● Brest        │                          │
│  └────────────────────────────────────┘                          │
│                                                                   │
│  ANOMALIES PASSÉES (7 derniers jours)                            │
│  ──────────────────────────────────────                          │
│  ┌─────────┬──────────────────────┬────────┐                     │
│  │ Date    │ Type                 │ Score  │                     │
│  ├─────────┼──────────────────────┼────────┤                     │
│  │31/12 12h│SPEED_SPIKE           │ 🔴 0.85│                     │
│  │30/12 16h│VELOCITY_VARIANCE_HIGH│ 🟠 0.62│                     │
│  │28/12 09h│HEADING_CHANGE        │ 🟠 0.58│                     │
│  └─────────┴──────────────────────┴────────┘                     │
│                                                                   │
│  [⬇️ Exporter CSV]  [📄 Générer Rapport PDF]                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Flux Utilisateur

### Flux 1 : Investigation d'Anomalie

```
1. Analyste se connecte → Dashboard
2. Voit widget "Anomalies récentes" → MAERSK ESSEX (score 0.85)
3. Clic sur "Détails" → Popup navire s'ouvre
4. Lit raisons : SPEED_SPIKE + SPOOFING_IMPOSSIBLE_SPEED
5. Clic "Voir Historique" → Graphique vitesse montre pic brutal
6. Décision : Investigation approfondie nécessaire
7. Clic "Épingler" → Navire ajouté à liste de surveillance
8. Clic "Notifier email" → Envoi rapport au superviseur
```

### Flux 2 : Identification Zone à Risque

```
1. Superviseur accède à la carte
2. Active layer "Heatmap" (toggle)
3. Configure : Résolution 10km, Période 7 jours
4. Identifie zone rouge dans le détroit de Douvres
5. Clic sur cellule rouge → 47 anomalies
6. Filtre "Type: Spoofing" → 15 cas de spoofing
7. Export CSV de la zone
8. Partage avec équipe d'investigation
```

### Flux 3 : Recherche Navire Spécifique

```
1. Opérateur SAR reçoit appel radio : MMSI 123456789
2. Tape "123456789" dans barre de recherche
3. Résultat : MAERSK ESSEX trouvé
4. Carte se centre automatiquement sur le navire
5. Popup s'ouvre avec position actuelle
6. Lit : 48°14'N, 005°31'W, Cap 245°, 12.5kt
7. Communique position à équipe terrain
```

---

## Composants Réutilisables (Frontend)

### VesselMarker.vue
Marqueur de navire sur la carte avec icône dynamique, couleur selon statut, rotation selon cap.

### VesselPopup.vue
Popup détaillé d'un navire avec photo, infos, anomalies.

### AnomalyBadge.vue
Badge coloré affichant score d'anomalie (vert/orange/rouge).

### Heatmap.vue
Composant de heatmap avec configuration (résolution, période, filtres).

### Dashboard Widget.vue
Widget de dashboard (navires actifs, métriques, graphiques).

### NotificationToast.vue
Toast notification temps réel pour nouvelles anomalies.

### SearchBar.vue
Barre de recherche avec autocomplétion.

### FilterPanel.vue
Panneau de filtres (type navire, statut, vitesse, etc.).

---

**Fin du document User Stories & Wireframes**
