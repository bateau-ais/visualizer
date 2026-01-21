<script setup lang="ts">
import { BookOpen, AlertTriangle, TrendingUp, Navigation, MapPin, Wifi, Shield } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'

interface AnomalyType {
  id: string
  name: string
  icon: any
  severity: 'high' | 'medium' | 'low'
  description: string
  examples: string[]
  causes: string[]
  actions: string[]
  monitored: boolean
}

const anomalyTypes: AnomalyType[] = [
  {
    id: 'speed',
    name: 'Anomalie de Vitesse',
    icon: TrendingUp,
    severity: 'medium',
    monitored: true,
    description: 'Vitesse incohérente avec le profil historique du navire (Z-score > 2.5σ) ou variation brusque non justifiée (Speed Spike).',
    examples: [
      'Variation instantanée > 5 nœuds (Seuil IMO SOLAS V/19)',
      'Vitesse < 0.5 nœuds en haute mer (Arrêt inexpliqué)',
      'Déviation significative par rapport à la moyenne historique (30 jours)'
    ],
    causes: [
      'Manœuvre d\'urgence ou évitement',
      'Dérive suite à avarie propulsion',
      'Dysfonctionnement capteur loch/GPS',
      'Falsification de données (Spoofing)'
    ],
    actions: [
      'Vérifier la cohérence avec le profil cinématique du navire',
      'Analyser l\'historique de vitesse sur 24h',
      'Corréler avec les conditions météo (État de mer)'
    ]
  },
  {
    id: 'course',
    name: 'Anomalie de Trajectoire',
    icon: Navigation,
    severity: 'medium',
    monitored: true,
    description: 'Évolution du navire incohérente avec les normes de navigation ou la réglementation (COLREGs).',
    examples: [
      'Changement de cap > 90° non justifié (COLREGS Rule 8b)',
      'Navigation en zigzag (Variance de cap élevée > 50 deg²)',
      'Dérive latérale importante'
    ],
    causes: [
      'Manœuvre d\'évitement (Collision avoidance)',
      'Perte de manœuvrabilité',
      'Conditions météorologiques dégradées',
      'Comportement suspect (Contrebande, Transbordement)'
    ],
    actions: [
      'Consulter les données radar/ARPA si disponibles',
      'Vérifier la densité du trafic environnant',
      'Surveiller l\'évolution du CPA/TCPA avec les navires proches'
    ]
  },
  {
    id: 'heading',
    name: 'Incohérence Cap/Route',
    icon: Navigation,
    severity: 'low',
    monitored: false,
    description: 'Divergence significative entre le cap gyro (Heading) et la route fond (COG), suggérant une dérive ou une erreur instrumentale.',
    examples: [
      'Différence |Heading - COG| > 30° durable',
      'Cap stable mais variation forte de la route fond',
      'Indication de giration sans changement de cap'
    ],
    causes: [
      'Forte dérive (Courant/Vent)',
      'Défaillance compas ou gyro',
      'Erreur de calibration AIS',
      'Manipulation GNSS (Spoofing)'
    ],
    actions: [
      'Vérifier les vecteurs vent/courant dans la zone',
      'Comparer avec les navires voisins (Flux)',
      'Identifier une potentielle défaillance senseur'
    ]
  },
  {
    id: 'spoofing',
    name: 'Suspicion Spoofing GNSS',
    icon: AlertTriangle,
    severity: 'high',
    monitored: true,
    description: 'Incohérences cinématiques majeures indiquant une probable falsification du signal de positionnement ou des données AIS.',
    examples: [
      'Vitesse > Vitesse max théorique du type de navire',
      'Vitesse absolue > 50 nœuds (Hors navires rapides)',
      'Sauts de position impossibles (Téléportation)',
      'Positions multiples simultanées (Identity theft)'
    ],
    causes: [
      'Attaque par usurpation GNSS (Spoofing)',
      'Piratage du transpondeur AIS',
      'Warfare électronique',
      'Dysfonctionnement critique du récepteur GNSS'
    ],
    actions: [
      'RAPPORT PRIORITAIRE - Alerter le commandement',
      'Valider la position par source non-GNSS (Radar, Optique)',
      'Analyser la cohérence des messages de position',
      'Vérifier intégrité des données statiques'
    ]
  },
  {
    id: 'position',
    name: 'Discontinuité de Position',
    icon: MapPin,
    severity: 'high',
    monitored: true,
    description: 'Déplacement calculé physiquement impossible entre deux rapports de position consécutifs (Vitesse implicite irréaliste).',
    examples: [
      'Delta distance incompatible avec delta temps (V > 100 kts)',
      'Saut géographique trans-régional instantané',
      'Lat/Long invalides ou hors limites'
    ],
    causes: [
      'Erreur de décodage/transmission AIS',
      'Perte temporaire de signal GPS',
      'Spoofing (Rejeu de trames)',
      'Bug firmware transpondeur'
    ],
    actions: [
      'Vérifier le timestamp des messages',
      'Filtrer les points aberrants',
      'Rechercher des traces de manipulation'
    ]
  },
  {
    id: 'communication',
    name: 'Perte de Signal (Gap)',
    icon: Wifi,
    severity: 'medium',
    monitored: false,
    description: 'Absence de réception AIS dépassant le seuil de tolérance pour la classe du navire et la zone de couverture.',
    examples: [
      'Silence > 3x intervalle de report nominal',
      'Disparition soudaine en zone de couverture nominale',
      'Réapparition inattendue avec saut de position'
    ],
    causes: [
      'Extinction volontaire du transpondeur (Dark ship)',
      'Zone d\'ombre de couverture',
      'Saturation du canal AIS',
      'Avarie électrique/radio'
    ],
    actions: [
      'Vérifier la couverture théorique de la zone',
      'Consulter les dernières positions connues',
      'Déclencher une recherche active (Radar/Visuelle) si critique'
    ]
  },
  {
    id: 'zone',
    name: 'Violation de Zone',
    icon: Shield,
    severity: 'high',
    monitored: true,
    description: 'Présence détectée dans une zone à accès réglementé ou incompatible avec le statut du navire.',
    examples: [
      'Entrée en ZEE sans autorisation',
      'Traversée d\'aire marine protégée (AMP) à vitesse inadaptée',
      'Mouillage en zone interdite (Câbles, Pipelines)',
      'Loitering suspect > 2h hors zone d\'attente'
    ],
    causes: [
      'Navigation négligente',
      'Activités illicites (Pêche, Rejet, Contrebande)',
      'Force majeure (Météo, Avarie)',
      'Incursion délibérée'
    ],
    actions: [
      'Vérifier le statut légal et les autorisations',
      'Initier procédure d\'interrogation radio',
      'Documenter la violation (Preuve légale)',
      'Alerter les autorités compétentes (CROSS/Gendarmerie)'
    ]
  }
]

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'default'
    default: return 'default'
  }
}
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-3">
        <BookOpen class="w-8 h-8 text-accent-primary" />
        <h1 class="text-3xl font-bold text-text-primary">Référentiel des Anomalies</h1>
      </div>
      <p class="text-text-secondary text-lg">
        Définitions techniques et procédures opérationnelles pour les anomalies détectées par le système NOVA.
      </p>
    </div>

    <!-- Introduction Card -->
    <Card>
      <div class="space-y-3">
        <h2 class="text-xl font-semibold text-text-primary">Algorithme de Détection</h2>
        <p class="text-text-secondary">
          Le moteur d'analyse NOVA utilise une approche <strong>multi-critères</strong> combinant analyse statistique (Z-scores), 
          règles cinématiques (SOLAS/COLREGS) et détection d'incohérences physiques.
          Chaque détection génère un <strong>Score de Confiance</strong> déterminant la criticité de l'alerte.
        </p>
        <div class="flex flex-wrap gap-2 mt-4">
          <Badge variant="danger" size="sm">Score ≥ 80% : Anomalie Critique (Action Requise)</Badge>
          <Badge variant="warning" size="sm">Score 50-79% : Avertissement (À surveiller)</Badge>
          <Badge variant="default" size="sm">Score < 50% : Signal faible</Badge>
        </div>
      </div>
    </Card>

    <!-- Anomaly Types -->
    <div class="space-y-4">
      <h2 class="text-2xl font-bold text-text-primary mb-4">Classification des Anomalies</h2>
      
      <Card  
        v-for="anomaly in anomalyTypes" 
        :key="anomaly.id"
        class="hover:border-accent-primary/30 transition-colors"
      >
        <div class="space-y-4">
          <!-- Title -->
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="p-2 rounded-lg bg-bg-primary">
                <component :is="anomaly.icon" class="w-6 h-6 text-accent-primary" />
              </div>
              <div>
                <h3 class="text-xl font-semibold text-text-primary">{{ anomaly.name }}</h3>
                <Badge :variant="getSeverityColor(anomaly.severity)" size="sm" class="mt-1">
                  Priorité : {{ anomaly.severity === 'high' ? 'Haute' : anomaly.severity === 'medium' ? 'Moyenne' : 'Basse' }}
                </Badge>
                <Badge v-if="!anomaly.monitored" variant="default" className="bg-gray-500 text-white" size="sm" class="mt-1 ml-2">
                  Non Surveillé
                </Badge>
              </div>
            </div>
          </div>

          <!-- Description -->
          <p class="text-text-secondary font-medium">{{ anomaly.description }}</p>

          <!-- Grid for Details -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <!-- Examples -->
            <div>
              <h4 class="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                <span>📋</span> Indicateurs
              </h4>
              <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
                <li v-for="(example, i) in anomaly.examples" :key="i">{{ example }}</li>
              </ul>
            </div>

            <!-- Causes -->
            <div>
              <h4 class="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                <span>🔍</span> Hypothèses
              </h4>
              <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
                <li v-for="(cause, i) in anomaly.causes" :key="i">{{ cause }}</li>
              </ul>
            </div>

            <!-- Actions -->
            <div class="bg-bg-primary/50 p-3 rounded-lg">
              <h4 class="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                <span>✅</span> Procédure
              </h4>
              <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
                <li v-for="(action, i) in anomaly.actions" :key="i">{{ action }}</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>


  </div>
</template>
