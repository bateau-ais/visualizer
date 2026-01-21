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
    name: 'Speed Anomaly',
    icon: TrendingUp,
    severity: 'medium',
    monitored: true,
    description: 'Speed inconsistent with vessel historical profile (Z-score > 2.5σ) or unjustified sudden variation (Speed Spike).',
    examples: [
      'Instantaneous variation > 5 knots (IMO SOLAS V/19 Threshold)',
      'Speed < 0.5 knots in open sea (Unexplained stop)',
      'Significant deviation from historical average (30 days)'
    ],
    causes: [
      'Emergency maneuver or avoidance',
      'Drift due to propulsion failure',
      'Log/GPS sensor malfunction',
      'Data falsification (Spoofing)'
    ],
    actions: [
      'Check consistency with vessel kinematic profile',
      'Analyze speed history over 24h',
      'Correlate with weather conditions (Sea state)'
    ]
  },
  {
    id: 'course',
    name: 'Trajectory Anomaly',
    icon: Navigation,
    severity: 'medium',
    monitored: true,
    description: 'Vessel evolution inconsistent with navigation standards or regulations (COLREGs).',
    examples: [
      'Course change > 90° unjustified (COLREGS Rule 8b)',
      'Zigzag navigation (High heading variance > 50 deg²)',
      'Significant lateral drift'
    ],
    causes: [
      'Avoidance maneuver (Collision avoidance)',
      'Loss of maneuverability',
      'Degraded weather conditions',
      'Suspicious behavior (Smuggling, Transshipment)'
    ],
    actions: [
      'Consult Radar/ARPA data if available',
      'Check surrounding traffic density',
      'Monitor CPA/TCPA evolution with nearby vessels'
    ]
  },
  {
    id: 'heading',
    name: 'Heading/Course Inconsistency',
    icon: Navigation,
    severity: 'low',
    monitored: false,
    description: 'Significant divergence between gyro heading (Heading) and course over ground (COG), suggesting drift or instrumental error.',
    examples: [
      'Difference |Heading - COG| > 30° sustained',
      'Stable heading but strong variation in course over ground',
      'Indication of turning without heading change'
    ],
    causes: [
      'Strong drift (Current/Wind)',
      'Compass or gyro failure',
      'AIS calibration error',
      'GNSS manipulation (Spoofing)'
    ],
    actions: [
      'Check wind/current vectors in the area',
      'Compare with neighboring vessels (Flow)',
      'Identify potential sensor failure'
    ]
  },
  {
    id: 'spoofing',
    name: 'GNSS Spoofing Suspicion',
    icon: AlertTriangle,
    severity: 'high',
    monitored: true,
    description: 'Major kinematic inconsistencies indicating probable falsification of positioning signal or AIS data.',
    examples: [
      'Speed > Max theoretical speed of vessel type',
      'Absolute speed > 50 knots (Excluding fast vessels)',
      'Impossible position jumps (Teleportation)',
      'Simultaneous multiple positions (Identity theft)'
    ],
    causes: [
      'GNSS spoofing attack',
      'AIS transponder hacking',
      'Electronic warfare',
      'Critical GNSS receiver malfunction'
    ],
    actions: [
      'PRIORITY REPORT - Alert command',
      'Validate position via non-GNSS source (Radar, Optical)',
      'Analyze position message consistency',
      'Verify static data integrity'
    ]
  },
  {
    id: 'position',
    name: 'Position Discontinuity',
    icon: MapPin,
    severity: 'high',
    monitored: true,
    description: 'Calculated displacement physically impossible between two consecutive position reports (Unrealistic implicit speed).',
    examples: [
      'Delta distance incompatible with delta time (V > 100 kts)',
      'Instantaneous trans-regional geographic jump',
      'Invalid Lat/Long or out of bounds'
    ],
    causes: [
      'AIS decoding/transmission error',
      'Temporary GPS signal loss',
      'Spoofing (Frame replay)',
      'Transponder firmware bug'
    ],
    actions: [
      'Check message timestamp',
      'Filter outliers',
      'Search for signs of manipulation'
    ]
  },
  {
    id: 'communication',
    name: 'Signal Loss (Gap)',
    icon: Wifi,
    severity: 'medium',
    monitored: false,
    description: 'Absence of AIS reception exceeding tolerance threshold for vessel class and coverage area.',
    examples: [
      'Silence > 3x nominal reporting interval',
      'Sudden disappearance in nominal coverage area',
      'Unexpected reappearance with position jump'
    ],
    causes: [
      'Voluntary transponder switch-off (Dark ship)',
      'Coverage shadow zone',
      'AIS channel saturation',
      'Electrical/radio failure'
    ],
    actions: [
      'Check theoretical area coverage',
      'Consult last known positions',
      'Trigger active search (Radar/Visual) if critical'
    ]
  },
  {
    id: 'zone',
    name: 'Zone Violation',
    icon: Shield,
    severity: 'high',
    monitored: true,
    description: 'Presence detected in a restricted access zone or incompatible with vessel status.',
    examples: [
      'Unauthorized entry into EEZ',
      'Crossing Marine Protected Area (MPA) at inappropriate speed',
      'Anchoring in prohibited area (Cables, Pipelines)',
      'Suspicious loitering > 2h outside holding area'
    ],
    causes: [
      'Negligent navigation',
      'Illicit activities (Fishing, Dumping, Smuggling)',
      'Force majeure (Weather, Damage)',
      'Deliberate incursion'
    ],
    actions: [
      'Verify legal status and authorizations',
      'Initiate radio interrogation procedure',
      'Document violation (Legal proof)',
      'Alert competent authorities (Coast Guard)'
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
        <h1 class="text-3xl font-bold text-text-primary">Anomaly Reference Guide</h1>
      </div>
      <p class="text-text-secondary text-lg">
        Technical definitions and operational procedures for anomalies detected by the NOVA system.
      </p>
    </div>

    <!-- Introduction Card -->
    <Card>
      <div class="space-y-3">
        <h2 class="text-xl font-semibold text-text-primary">Detection Algorithm</h2>
        <p class="text-text-secondary">
          The NOVA analysis engine uses a <strong>multi-criteria</strong> approach combining statistical analysis (Z-scores), 
          kinematic rules (SOLAS/COLREGS), and physical inconsistency detection.
          Each detection generates a <strong>Confidence Score</strong> determining the alert criticality.
        </p>
        <div class="flex flex-wrap gap-2 mt-4">
          <Badge variant="danger" size="sm">Score ≥ 80% : Critical Anomaly (Action Required)</Badge>
          <Badge variant="warning" size="sm">Score 50-79% : Warning (To monitor)</Badge>
          <Badge variant="default" size="sm">Score < 50% : Weak Signal</Badge>
        </div>
      </div>
    </Card>

    <!-- Anomaly Types -->
    <div class="space-y-4">
      <h2 class="text-2xl font-bold text-text-primary mb-4">Anomaly Classification</h2>
      
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
                  Priority : {{ anomaly.severity === 'high' ? 'High' : anomaly.severity === 'medium' ? 'Medium' : 'Low' }}
                </Badge>
                <Badge v-if="!anomaly.monitored" variant="default" className="bg-gray-500 text-white" size="sm" class="mt-1 ml-2">
                  Not Monitored
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
                Indicators
              </h4>
              <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
                <li v-for="(example, i) in anomaly.examples" :key="i">{{ example }}</li>
              </ul>
            </div>

            <!-- Causes -->
            <div>
              <h4 class="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                Hypotheses
              </h4>
              <ul class="list-disc list-inside space-y-1 text-sm text-text-secondary">
                <li v-for="(cause, i) in anomaly.causes" :key="i">{{ cause }}</li>
              </ul>
            </div>

            <!-- Actions -->
            <div class="bg-bg-primary/50 p-3 rounded-lg">
              <h4 class="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                Procedure
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
