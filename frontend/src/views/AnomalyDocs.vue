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
}

const anomalyTypes: AnomalyType[] = [
  {
    id: 'speed',
    name: 'Speed Anomaly',
    icon: TrendingUp,
    severity: 'medium',
    description: 'Détectée lorsqu\'un navire navigue à une vitesse anormalement élevée ou basse par rapport à son type et à ses conditions habituelles.',
    examples: [
      'Un cargo naviguant à plus de 25 nœuds (vitesse inhabituelle pour ce type)',
      'Un navire de pêche complètement immobile pendant plusieurs heures dans une zone de navigation active',
      'Changements brusques de vitesse sans raison apparente'
    ],
    causes: [
      'Urgence médicale ou technique',
      'Activités de pêche illégale',
      'Tentative d\'éviter la détection',
      'Problèmes moteur'
    ],
    actions: [
      'Vérifier l\'historique de vitesse du navire',
      'Comparer avec les navires similaires dans la zone',
      'Contacter le navire si nécessaire'
    ]
  },
  {
    id: 'course',
    name: 'Course Anomaly',
    icon: Navigation,
    severity: 'medium',
    description: 'Changement soudain et inexpliqué de la trajectoire ou du cap du navire, pouvant indiquer une manœuvre d\'évitement ou un comportement suspect.',
    examples: [
      'Changement de cap de plus de 90° sans raison apparente',
      'Navigation en zigzag dans une zone normalement droite',
      'Déviation soudaine de la route maritime établie'
    ],
    causes: [
      'Évitement d\'obstacles ou d\'autres navires',
      'Conditions météorologiques',
      'Activités de contrebande',
      'Problèmes de navigation'
    ],
    actions: [
      'Analyser le contexte de la zone (météo, trafic)',
      'Vérifier s\'il y avait d\'autres navires à proximité',
      'Examiner la trajectoire complète sur 24h'
    ]
  },
  {
    id: 'heading',
    name: 'Heading Anomaly',
    icon: Navigation,
    severity: 'low',
    description: 'Incohérence entre le cap (heading) et la direction réelle du mouvement (course over ground), ce qui peut indiquer des problèmes de navigation ou de transmission.',
    examples: [
      'Le navire pointe vers le nord mais se déplace vers l\'est',
      'Différence persistante de plus de 30° entre heading et COG',
      'Cap changeant rapidement alors que la trajectoire reste stable'
    ],
    causes: [
      'Courants marins forts',
      'Problèmes de gouvernail',
      'Erreurs de transmission AIS',
      'Manœuvres spéciales'
    ],
    actions: [
      'Vérifier les conditions de courant dans la zone',
      'Comparer avec les données historiques du navire',
      'Évaluer si c\'est un problème technique AIS'
    ]
  },
  {
    id: 'spoofing',
    name: 'GPS Spoofing Suspected',
    icon: AlertTriangle,
    severity: 'high',
    description: 'Suspicion de falsification de la position GPS, une technique utilisée pour masquer la position réelle du navire. Ceci est extrêmement grave et peut indiquer des activités illégales.',
    examples: [
      'Navire rapportant être dans un port alors qu\'il est en mer',
      'Sauts de position impossibles (téléportation)',
      'Plusieurs navires rapportant exactement la même position',
      'Position rapportée sur terre ferme'
    ],
    causes: [
      'Tentative délibérée de falsification',
      'Activités de contrebande',
      'Violations de sanctions',
      'Pêche illégale'
    ],
    actions: [
      'PRIORITÉ HAUTE - Signaler immédiatement',
      'Corréler avec d\'autres sources (radar, satellite)',
      'Vérifier l\'historique complet du navire',
      'Contacter les autorités maritimes'
    ]
  },
  {
    id: 'position',
    name: 'Position Discontinuity',
    icon: MapPin,
    severity: 'high',
    description: 'Saut de position géographiquement impossible compte tenu de la vitesse du navire, suggérant une erreur de transmission ou une falsification.',
    examples: [
      'Navire passant de la Méditerranée à l\'Atlantique en 5 minutes',
      'Sauts de plus de 100 milles nautiques entre deux transmissions consécutives',
      'Téléportation d\'un point A à un point B distant'
    ],
    causes: [
      'Falsification GPS',
      'Erreur de transmission AIS',
      'Problème de réception du signal',
      'Échange d\'identité entre navires (identity swapping)'
    ],
    actions: [
      'Vérifier la continuité des transmissions',
      'Analyser les positions précédentes et suivantes',
      'Rechercher des patterns de spoofing',
      'Signaler si la discontinuité persiste'
    ]
  },
  {
    id: 'communication',
    name: 'Communication Gap',
    icon: Wifi,
    severity: 'medium',
    description: 'Interruption anormalement longue des transmissions AIS, pouvant indiquer que le transpondeur a été volontairement éteint ou qu\'il y a un problème technique.',
    examples: [
      'Absence de signal pendant plus de 6 heures en haute mer',
      'Coupures répétées dans une zone avec bonne couverture',
      'Silence radio suivi d\'une réapparition dans un autre port'
    ],
    causes: [
      'Transpondeur volontairement éteint',
      'Problèmes techniques',
      'Activités de transbordement illégal',
      'Zones de faible couverture (rare)'
    ],
    actions: [
      'Noter la durée et la fréquence des coupures',
      'Vérifier la zone de disparition',
      'Analyser le comportement avant et après la coupure',
      'Escalader si les coupures sont fréquentes'
    ]
  },
  {
    id: 'zone',
    name: 'Zone Violation',
    icon: Shield,
    severity: 'high',
    description: 'Entrée du navire dans une zone maritime interdite, protégée, ou soumise à restrictions sans autorisation apparente.',
    examples: [
      'Entrée dans une zone de pêche protégée',
      'Navigation dans des eaux territoriales sans autorisation',
      'Présence dans une zone de conflit ou sous embargo',
      'Approche non autorisée d\'infrastructures critiques'
    ],
    causes: [
      'Violation délibérée',
      'Erreur de navigation',
      'Conditions météo forcing deviation',
      'Activités illégales (pêche, contrebande)'
    ],
    actions: [
      'Vérifier immédiatement les autorisations du navire',
      'Contacter le navire pour clarification',
      'Alerter les garde-côtes si nécessaire',
      'Documenter la durée et le trajet dans la zone'
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
        <h1 class="text-3xl font-bold text-text-primary">Guide des Types d'Anomalies</h1>
      </div>
      <p class="text-text-secondary text-lg">
        Comprendre les différents types d'anomalies détectées par le système NOVA de surveillance maritime.
      </p>
    </div>

    <!-- Introduction Card -->
    <Card>
      <div class="space-y-3">
        <h2 class="text-xl font-semibold text-text-primary">Comment fonctionne la détection d'anomalies ?</h2>
        <p class="text-text-secondary">
          Le système NOVA analyse en temps réel les données AIS (Automatic Identification System) de tous les navires 
          pour détecter des comportements inhabituels ou suspects. Chaque anomalie est classifiée selon son type et 
          se voit attribuer un score de confiance.
        </p>
        <div class="flex flex-wrap gap-2 mt-4">
          <Badge variant="danger" size="sm">Score ≥ 80% : Critique</Badge>
          <Badge variant="warning" size="sm">Score 50-79% : Attention</Badge>
          <Badge variant="default" size="sm">Score < 50% : Information</Badge>
        </div>
      </div>
    </Card>

    <!-- Anomaly Types -->
    <div class="space-y-4">
      <h2 class="text-2xl font-bold text-text-primary mb-4">Types d'Anomalies</h2>
      
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
                  Gravité : {{ anomaly.severity === 'high' ? 'Haute' : anomaly.severity === 'medium' ? 'Moyenne' : 'Faible' }}
                </Badge>
              </div>
            </div>
          </div>

          <!-- Description -->
          <p class="text-text-secondary">{{ anomaly.description }}</p>

          <!-- Examples -->
          <div>
            <h4 class="text-sm font-semibold text-text-primary mb-2">📋 Exemples concrets :</h4>
            <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
              <li v-for="(example, i) in anomaly.examples" :key="i">{{ example }}</li>
            </ul>
          </div>

          <!-- Causes -->
          <div>
            <h4 class="text-sm font-semibold text-text-primary mb-2">🔍 Causes possibles :</h4>
            <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
              <li v-for="(cause, i) in anomaly.causes" :key="i">{{ cause }}</li>
            </ul>
          </div>

          <!-- Actions -->
          <div class="bg-bg-primary p-3 rounded-lg">
            <h4 class="text-sm font-semibold text-text-primary mb-2">✅ Actions recommandées :</h4>
            <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
              <li v-for="(action, i) in anomaly.actions" :key="i">{{ action }}</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>


  </div>
</template>
