# NOVA Visualizer Frontend

Modern web interface for maritime anomaly detection visualization.

## Tech Stack

-**Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build**: Vite 5
- **Styling**: Tailwind CSS (dark maritime theme)
- **State**: Pinia
- **Maps**: Leaflet
- **Charts**: Apache ECharts
- **Icons**: Lucide Icons

## Development

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── main.ts                 # App entry point
├── App.vue                 # Root component
├── router/                 # Vue Router
├── stores/                 # Pinia stores
├── composables/            # Composables (useWebSocket, etc.)
├── components/
│   ├── ui/                 # Base UI components
│   ├── layout/             # Layout components
│   ├── map/                # Map components (TODO)
│   ├── vessel/             # Vessel components (TODO)
│   └── dashboard/          # Dashboard widgets (TODO)
├── views/                  # Page views (TODO)
├── utils/                  # Utilities
├── types/                  # TypeScript types
└── assets/                 # Styles, images
```

## Available Components

### UI Components
- `Button` - Reusable button with variants
- `Card` - Container card
- `Badge` - Status badge with dot
- `Input` - Form input
- `Select` - Dropdown select

### Layout Components
- `Navbar` - Top navigation with search
- `Sidebar` - Filter sidebar (collapsible)
- `NotificationCenter` - Toast notifications

## Color Theme

See `tailwind.config.js` for full color palette.

### Status Colors
- **Green** (`#10b981`) - Normal vessel
- **Orange** (`#f59e0b`) - Anomaly warning
- **Red** (`#ef4444`) - Critical anomaly
- **Cyan** (`#00d4ff`) - Selected vessel
- **Gray** (`#6b7280`) - Stale data

## API Integration

Backend API runs on `http://localhost:8000`.  
Vite proxy is configured to forward `/api` and `/ws` requests.
