#!/bin/bash

# Zmarty Dashboard Domain Setup Script
# Configure production domain and DNS settings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}    🌐 ZMARTY DOMAIN CONFIGURATION      ${NC}"
    echo -e "${PURPLE}============================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to validate domain name
validate_domain() {
    local domain="$1"
    if [[ $domain =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check DNS resolution
check_dns() {
    local domain="$1"
    local record_type="$2"
    
    print_info "Checking $record_type record for $domain..."
    
    if nslookup -type=$record_type "$domain" >/dev/null 2>&1; then
        local result=$(nslookup -type=$record_type "$domain" | grep -A 10 "Name:" | grep "Address" | head -1 | awk '{print $2}')
        if [ -n "$result" ]; then
            print_success "$record_type record found: $result"
            return 0
        fi
    fi
    
    print_warning "$record_type record not found or not propagated yet"
    return 1
}

# Function to generate Nginx configuration for domain
generate_nginx_config() {
    local domain="$1"
    local api_domain="$2"
    
    print_info "Generating Nginx configuration for $domain..."
    
    cat > nginx/nginx-production.conf << EOF
# Zmarty Dashboard Production Nginx Configuration
# Domain: $domain

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

# Upstream servers
upstream backend {
    server backend:8000;
    keepalive 32;
}

upstream frontend {
    server frontend:80;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $domain $api_domain;
    
    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# Main application server (HTTPS)
server {
    listen 443 ssl http2;
    server_name $domain;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/live/$domain/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/$domain/privkey.pem;
    ssl_trusted_certificate /etc/nginx/ssl/live/$domain/chain.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;
    
    # Root and index
    root /var/www/html;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Frontend static files
    location / {
        try_files \$uri \$uri/ @frontend;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }
    
    # Frontend fallback
    location @frontend {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # API endpoints
    location /api/ {
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket connections
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Security - Deny access to hidden files
    location ~ /\\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# API subdomain server (HTTPS)
server {
    listen 443 ssl http2;
    server_name $api_domain;
    
    # SSL Configuration (same as main domain)
    ssl_certificate /etc/nginx/ssl/live/$domain/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/$domain/privkey.pem;
    ssl_trusted_certificate /etc/nginx/ssl/live/$domain/chain.pem;
    
    # SSL Security Settings (same as above)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Access-Control-Allow-Origin "https://$domain" always;
    
    # API only - proxy everything to backend
    location / {
        # Rate limiting
        limit_req zone=api burst=50 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://$domain" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://$domain";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # WebSocket connections
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}

# Additional security server block for unknown domains
server {
    listen 80 default_server;
    listen 443 ssl http2 default_server;
    server_name _;
    
    # SSL Configuration for default server
    ssl_certificate /etc/nginx/ssl/default.pem;
    ssl_certificate_key /etc/nginx/ssl/default-key.pem;
    ssl_reject_handshake on;
    
    return 444;
}
EOF

    print_success "Nginx configuration generated: nginx/nginx-production.conf"
}

# Function to generate Docker Compose override for production
generate_docker_override() {
    local domain="$1"
    
    print_info "Generating Docker Compose production override..."
    
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  # Nginx with SSL and production configuration
  nginx:
    volumes:
      - ./nginx/nginx-production.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./certbot/www:/var/www/certbot
      - nginx_logs:/var/log/nginx
    environment:
      - DOMAIN=$domain
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nginx.rule=Host(\`$domain\`)"
      - "traefik.http.routers.nginx.tls=true"
      - "traefik.http.routers.nginx.tls.certresolver=letsencrypt"

  # Backend production configuration
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DATABASE_URL=postgresql://postgres:\${POSTGRES_PASSWORD}@postgres:5432/zmarty_dashboard
      - REDIS_URL=redis://:\${REDIS_PASSWORD}@redis:6379/0
      - BACKEND_CORS_ORIGINS=https://$domain,https://api.$domain
      - TRUSTED_HOSTS=$domain,api.$domain
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  # Frontend production configuration
  frontend:
    build:
      args:
        - VITE_API_BASE_URL=https://api.$domain/api/v1
        - VITE_WS_URL=wss://api.$domain/ws
        - VITE_STRIPE_PUBLISHABLE_KEY=\${VITE_STRIPE_PUBLISHABLE_KEY}
        - VITE_MCP_ENABLED=\${VITE_MCP_ENABLED:-true}
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # Database production configuration
  postgres:
    environment:
      - POSTGRES_DB=zmarty_dashboard
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # Redis production configuration
  redis:
    command: redis-server --appendonly yes --requirepass \${REDIS_PASSWORD} --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Certbot for SSL certificates
  certbot:
    image: certbot/certbot
    container_name: zmarty_certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: >
      sh -c "while :; do
        certbot renew --webroot --webroot-path=/var/www/certbot --email admin@$domain --agree-tos --no-eff-email;
        sleep 12h & wait \$\${!}; 
      done"
    restart: unless-stopped
    profiles:
      - ssl

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  nginx_logs:
    driver: local

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

    print_success "Docker Compose production override generated"
}

# Function to generate DNS instructions
generate_dns_instructions() {
    local domain="$1"
    local server_ip="$2"
    
    print_info "Generating DNS setup instructions..."
    
    cat > DNS_SETUP.md << EOF
# DNS Configuration for $domain

## Required DNS Records

Add the following DNS records to your domain registrar or DNS provider:

### A Records (IPv4)
\`\`\`
$domain               A    $server_ip
api.$domain           A    $server_ip
www.$domain           A    $server_ip
\`\`\`

### AAAA Records (IPv6) - Optional but recommended
\`\`\`
$domain               AAAA  [your-ipv6-address]
api.$domain           AAAA  [your-ipv6-address] 
www.$domain           AAAA  [your-ipv6-address]
\`\`\`

### CNAME Records
\`\`\`
www.$domain           CNAME $domain
\`\`\`

### Additional Records (Optional)

#### MX Record (for email)
\`\`\`
$domain               MX    10 mail.$domain
\`\`\`

#### TXT Records (for verification and security)
\`\`\`
$domain               TXT   "v=spf1 include:_spf.google.com ~all"
_dmarc.$domain        TXT   "v=DMARC1; p=none; rua=mailto:admin@$domain"
\`\`\`

## Verification

After setting up DNS records, verify them using:

\`\`\`bash
# Check A record
dig $domain A

# Check API subdomain
dig api.$domain A

# Check propagation
nslookup $domain 8.8.8.8
\`\`\`

## SSL Certificate Setup

Once DNS is propagated, run:

\`\`\`bash
# Generate SSL certificates
./scripts/setup-ssl.sh $domain

# Or using Docker
docker-compose --profile ssl up certbot
\`\`\`

## Cloudflare Setup (Recommended)

If using Cloudflare:

1. Add your domain to Cloudflare
2. Update nameservers at your registrar
3. Set SSL/TLS mode to "Full (strict)"
4. Enable "Always Use HTTPS"
5. Configure these Page Rules:
   - \`api.$domain/*\` → Cache Level: Bypass
   - \`$domain/api/*\` → Cache Level: Bypass
   - \`$domain/ws/*\` → Cache Level: Bypass

## Security Considerations

1. Enable HSTS
2. Configure proper CORS origins
3. Set up rate limiting
4. Monitor SSL certificate expiration
5. Regular security updates

Generated on: $(date)
EOF

    print_success "DNS setup instructions generated: DNS_SETUP.md"
}

# Function to update environment files with domain
update_env_files() {
    local domain="$1"
    local api_domain="$2"
    
    print_info "Updating environment files with domain configuration..."
    
    # Update backend .env
    if [ -f "backend/.env" ]; then
        # Update CORS origins
        sed -i.bak "s|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=https://$domain,https://$api_domain|" backend/.env
        # Update trusted hosts
        if grep -q "TRUSTED_HOSTS" backend/.env; then
            sed -i.bak "s|TRUSTED_HOSTS=.*|TRUSTED_HOSTS=$domain,$api_domain,localhost,127.0.0.1|" backend/.env
        else
            echo "TRUSTED_HOSTS=$domain,$api_domain,localhost,127.0.0.1" >> backend/.env
        fi
        print_success "Updated backend/.env"
    fi
    
    # Update frontend .env.local
    if [ -f "frontend/.env.local" ]; then
        # Update API base URL
        sed -i.bak "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=https://$api_domain/api/v1|" frontend/.env.local
        # Update WebSocket URL
        sed -i.bak "s|VITE_WS_URL=.*|VITE_WS_URL=wss://$api_domain/ws|" frontend/.env.local
        print_success "Updated frontend/.env.local"
    fi
}

# Main function
main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the Zmarty Dashboard root directory"
        exit 1
    fi
    
    print_info "This script will configure your production domain for Zmarty Dashboard"
    echo ""
    
    # Get domain name
    while true; do
        read -p "Enter your production domain name (e.g., mydashboard.com): " DOMAIN
        
        if [ -z "$DOMAIN" ]; then
            print_error "Domain name is required"
            continue
        fi
        
        if validate_domain "$DOMAIN"; then
            break
        else
            print_error "Invalid domain name format"
            continue
        fi
    done
    
    # Set API subdomain
    API_DOMAIN="api.$DOMAIN"
    
    print_info "Domain: $DOMAIN"
    print_info "API Subdomain: $API_DOMAIN"
    
    # Get server IP
    print_step "Server IP Configuration"
    echo "Enter your server's public IP address:"
    read -p "Server IP: " SERVER_IP
    
    # Validate IP (basic check)
    if [[ ! $SERVER_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_warning "IP format may be invalid, but continuing..."
    fi
    
    echo ""
    print_step "Generating configuration files..."
    
    # Generate configurations
    generate_nginx_config "$DOMAIN" "$API_DOMAIN"
    generate_docker_override "$DOMAIN"
    generate_dns_instructions "$DOMAIN" "$SERVER_IP"
    update_env_files "$DOMAIN" "$API_DOMAIN"
    
    echo ""
    print_step "DNS Check"
    
    # Check if DNS is already configured
    read -p "Check DNS configuration now? (y/N): " check_dns_now
    if [[ $check_dns_now =~ ^[Yy]$ ]]; then
        check_dns "$DOMAIN" "A"
        check_dns "$API_DOMAIN" "A"
    fi
    
    echo ""
    print_success "🎉 Domain configuration completed!"
    echo ""
    print_info "Files generated:"
    echo "  ✓ nginx/nginx-production.conf - Production Nginx configuration"
    echo "  ✓ docker-compose.prod.yml - Production Docker Compose override"
    echo "  ✓ DNS_SETUP.md - DNS configuration instructions"
    echo ""
    print_info "Next steps:"
    echo "1. Configure DNS records as shown in DNS_SETUP.md"
    echo "2. Wait for DNS propagation (up to 48 hours)"
    echo "3. Generate SSL certificates: ./scripts/setup-ssl.sh $DOMAIN"
    echo "4. Deploy with: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
    echo ""
    print_warning "Make sure your server firewall allows ports 80 and 443"
}

# Run main function
main "$@"