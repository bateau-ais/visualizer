# =============================================================================
# Stage 1: Development (with hot-reload for fast iteration)
# =============================================================================
FROM oven/bun:1.1.13-alpine as dev

WORKDIR /app

# Copy package files first (better Docker layer caching)
COPY package.json ./

# Install ALL dependencies (including devDependencies)
RUN bun install

# Copy source files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run in dev mode with hot-reload
# Vite will watch for file changes and rebuild incrementally
CMD ["bun", "run", "dev", "--", "--host", "0.0.0.0"]

# =============================================================================
# Stage 2: Build stage (creates production bundle)
# =============================================================================
FROM oven/bun:1.1.13-alpine as build

WORKDIR /app

# Copy package files
COPY bun.lock package.json ./

# Install dependencies (production + dev for build tools)
RUN bun install

# Copy source files
COPY . .

# Build for production
RUN bun run build

# =============================================================================
# Stage 3: Production (minimal nginx serving static files)
# =============================================================================
FROM nginx:stable-alpine as production

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port  
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
