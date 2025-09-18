# Production Dockerfile for ZmartyChat
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/website /usr/share/nginx/html/website
COPY --from=builder /app/web-app /usr/share/nginx/html/web-app
COPY --from=builder /app/admin /usr/share/nginx/html/admin
COPY --from=builder /app/api-docs /usr/share/nginx/html/api-docs
COPY --from=builder /app/help-center /usr/share/nginx/html/help-center
COPY --from=builder /app/onboarding /usr/share/nginx/html/onboarding
COPY --from=builder /app/src /usr/share/nginx/html/src

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]