/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // Dark mode maritime theme
                'bg-primary': '#0a0e1a',
                'bg-secondary': '#141b2d',
                'bg-tertiary': '#1e293b',

                'text-primary': '#f1f5f9',
                'text-secondary': '#94a3b8',
                'text-muted': '#64748b',

                'accent-primary': '#00d4ff',
                'accent-warning': '#ff6b35',
                'accent-success': '#10b981',
                'accent-danger': '#ef4444',

                'vessel-normal': '#10b981',
                'vessel-warning': '#f59e0b',
                'vessel-danger': '#ef4444',
                'vessel-selected': '#00d4ff',
                'vessel-stale': '#6b7280',

                'map-water': '#0c1e3a',
                'map-land': '#1e2a3a',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
