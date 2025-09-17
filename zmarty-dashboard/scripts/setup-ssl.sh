#!/bin/bash

# SSL Certificate Setup Script for Zmarty Dashboard
# Supports Let's Encrypt (Certbot), Self-signed, and Custom certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
SSL_DIR="$PROJECT_ROOT/nginx/ssl"
DOMAIN=""
EMAIL=""
SSL_TYPE="letsencrypt"
STAGING=false
FORCE_RENEW=false

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

show_help() {
    cat << EOF
🔒 SSL Certificate Setup Script for Zmarty Dashboard

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -d, --domain DOMAIN     Domain name (required)
    -e, --email EMAIL       Email for Let's Encrypt notifications
    -t, --type TYPE         Certificate type: letsencrypt, self-signed, custom (default: letsencrypt)
    -s, --staging           Use Let's Encrypt staging environment for testing
    -f, --force             Force certificate renewal
    -h, --help              Show this help message

EXAMPLES:
    # Let's Encrypt certificate for production
    $0 -d yourdomain.com -e admin@yourdomain.com

    # Let's Encrypt certificate for testing (staging)
    $0 -d yourdomain.com -e admin@yourdomain.com --staging

    # Self-signed certificate for development
    $0 -d localhost --type self-signed

    # Custom certificate (prompts for files)
    $0 -d yourdomain.com --type custom

CERTIFICATE TYPES:
    letsencrypt   - Free SSL certificates from Let's Encrypt (recommended for production)
    self-signed   - Self-signed certificates (development only)
    custom        - Use your own certificate files

EOF
}

validate_domain() {
    local domain=$1
    
    # Basic domain validation
    if [[ ! "$domain" =~ ^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$ ]]; then
        print_error "Invalid domain format: $domain"
        return 1
    fi
    
    return 0
}

validate_email() {
    local email=$1
    
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        print_error "Invalid email format: $email"
        return 1
    fi
    
    return 0
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if running as root (needed for certbot)
    if [[ "$SSL_TYPE" == "letsencrypt" && $EUID -ne 0 ]]; then
        print_error "Let's Encrypt setup requires root privileges. Please run with sudo."
        exit 1
    fi
    
    # Create SSL directory
    mkdir -p "$SSL_DIR"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed."
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

setup_letsencrypt() {
    print_step "Setting up Let's Encrypt SSL certificate..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        print_status "Installing certbot..."
        
        if command -v apt-get &> /dev/null; then
            apt-get update
            apt-get install -y certbot python3-certbot-nginx
        elif command -v yum &> /dev/null; then
            yum install -y certbot python3-certbot-nginx
        elif command -v brew &> /dev/null; then
            brew install certbot
        else
            print_error "Unable to install certbot automatically. Please install it manually."
            exit 1
        fi
    fi
    
    # Prepare certbot arguments
    local certbot_args=(
        "certonly"
        "--standalone"
        "--agree-tos"
        "--non-interactive"
        "-d" "$DOMAIN"
    )
    
    if [[ -n "$EMAIL" ]]; then
        certbot_args+=("--email" "$EMAIL")
    else
        certbot_args+=("--register-unsafely-without-email")
    fi
    
    if [[ "$STAGING" == true ]]; then
        certbot_args+=("--staging")
        print_warning "Using Let's Encrypt staging environment"
    fi
    
    if [[ "$FORCE_RENEW" == true ]]; then
        certbot_args+=("--force-renewal")
    fi
    
    # Stop nginx if running (certbot needs port 80)
    print_status "Stopping nginx container if running..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop nginx 2>/dev/null || true
    
    # Run certbot
    print_status "Obtaining SSL certificate from Let's Encrypt..."
    if certbot "${certbot_args[@]}"; then
        print_status "Certificate obtained successfully!"
    else
        print_error "Failed to obtain certificate from Let's Encrypt"
        exit 1
    fi
    
    # Copy certificates to project directory
    local cert_path="/etc/letsencrypt/live/$DOMAIN"
    if [[ -d "$cert_path" ]]; then
        cp "$cert_path/fullchain.pem" "$SSL_DIR/$DOMAIN.crt"
        cp "$cert_path/privkey.pem" "$SSL_DIR/$DOMAIN.key"
        
        # Set proper permissions
        chmod 644 "$SSL_DIR/$DOMAIN.crt"
        chmod 600 "$SSL_DIR/$DOMAIN.key"
        
        print_status "Certificates copied to $SSL_DIR/"
    else
        print_error "Certificate directory not found: $cert_path"
        exit 1
    fi
    
    # Setup auto-renewal
    setup_auto_renewal
}

setup_self_signed() {
    print_step "Setting up self-signed SSL certificate..."
    
    # Check if openssl is available
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is required for self-signed certificates"
        exit 1
    fi
    
    # Generate self-signed certificate
    print_status "Generating self-signed certificate for $DOMAIN..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/$DOMAIN.key" \
        -out "$SSL_DIR/$DOMAIN.crt" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN" \
        -config <(
        echo '[dn]'
        echo "CN=$DOMAIN"
        echo '[req]'
        echo 'distinguished_name = dn'
        echo '[extensions]'
        echo 'subjectAltName=DNS:'$DOMAIN
        echo '[v3_req]'
        echo 'keyUsage=keyEncipherment,dataEncipherment'
        echo 'extendedKeyUsage=serverAuth'
        echo "subjectAltName=DNS:$DOMAIN"
        ) -extensions v3_req
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/$DOMAIN.crt"
    chmod 600 "$SSL_DIR/$DOMAIN.key"
    
    print_status "Self-signed certificate generated successfully!"
    print_warning "⚠️  Self-signed certificates will show security warnings in browsers"
    print_warning "⚠️  Use only for development purposes"
}

setup_custom() {
    print_step "Setting up custom SSL certificate..."
    
    echo "Please provide the paths to your SSL certificate files:"
    echo
    
    # Get certificate file
    while true; do
        read -p "Certificate file (.crt or .pem): " cert_file
        if [[ -f "$cert_file" ]]; then
            break
        else
            print_error "File not found: $cert_file"
        fi
    done
    
    # Get private key file
    while true; do
        read -p "Private key file (.key): " key_file
        if [[ -f "$key_file" ]]; then
            break
        else
            print_error "File not found: $key_file"
        fi
    done
    
    # Get chain file (optional)
    read -p "Certificate chain file (optional, press Enter to skip): " chain_file
    
    # Copy files
    print_status "Copying certificate files..."
    
    if [[ -n "$chain_file" && -f "$chain_file" ]]; then
        # Combine certificate and chain
        cat "$cert_file" "$chain_file" > "$SSL_DIR/$DOMAIN.crt"
    else
        cp "$cert_file" "$SSL_DIR/$DOMAIN.crt"
    fi
    
    cp "$key_file" "$SSL_DIR/$DOMAIN.key"
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/$DOMAIN.crt"
    chmod 600 "$SSL_DIR/$DOMAIN.key"
    
    print_status "Custom certificate installed successfully!"
}

setup_auto_renewal() {
    print_step "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > "$PROJECT_ROOT/scripts/renew-ssl.sh" << 'EOF'
#!/bin/bash

# SSL Certificate Renewal Script
# This script handles automatic renewal of Let's Encrypt certificates

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SSL_DIR="$PROJECT_ROOT/nginx/ssl"

echo "🔄 Checking for SSL certificate renewal..."

# Stop nginx
docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop nginx

# Renew certificates
if certbot renew --quiet; then
    echo "✅ Certificates renewed successfully"
    
    # Copy renewed certificates
    for domain_dir in /etc/letsencrypt/live/*/; do
        if [[ -d "$domain_dir" ]]; then
            domain=$(basename "$domain_dir")
            cp "$domain_dir/fullchain.pem" "$SSL_DIR/$domain.crt"
            cp "$domain_dir/privkey.pem" "$SSL_DIR/$domain.key"
            chmod 644 "$SSL_DIR/$domain.crt"
            chmod 600 "$SSL_DIR/$domain.key"
        fi
    done
    
    # Restart nginx
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" start nginx
    
    echo "🚀 SSL certificates renewed and nginx restarted"
else
    echo "ℹ️  No certificates needed renewal"
    # Start nginx back
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" start nginx
fi
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/renew-ssl.sh"
    
    # Add cron job for automatic renewal
    print_status "Setting up cron job for automatic renewal..."
    
    local cron_job="0 12 * * * $PROJECT_ROOT/scripts/renew-ssl.sh >> $PROJECT_ROOT/logs/ssl-renewal.log 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "renew-ssl.sh"; then
        print_warning "Cron job for SSL renewal already exists"
    else
        # Add cron job
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        print_status "Cron job added for automatic renewal (runs daily at 12:00)"
    fi
    
    print_status "Auto-renewal setup completed"
}

update_nginx_config() {
    print_step "Updating nginx configuration..."
    
    local nginx_config="$PROJECT_ROOT/nginx/nginx.conf"
    
    # Backup existing config
    if [[ -f "$nginx_config" ]]; then
        cp "$nginx_config" "$nginx_config.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Nginx config backed up"
    fi
    
    # Create SSL-enabled nginx configuration
    cat > "$nginx_config" << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate max-age=0;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;
    
    # Upstream servers
    upstream backend {
        server backend:8000;
        keepalive 32;
    }
    
    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }
    
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$server_name\$request_uri;
    }
    
    # Main HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/$DOMAIN.crt;
        ssl_certificate_key /etc/nginx/ssl/$DOMAIN.key;
        
        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        
        # Frontend (React)
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
            proxy_redirect off;
        }
        
        # Backend API
        location /api/ {
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
            proxy_redirect off;
            
            # Timeout settings
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
        
        # Static files
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            proxy_pass http://frontend;
        }
        
        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    print_status "Nginx configuration updated with SSL support"
}

verify_certificates() {
    print_step "Verifying SSL certificates..."
    
    local cert_file="$SSL_DIR/$DOMAIN.crt"
    local key_file="$SSL_DIR/$DOMAIN.key"
    
    if [[ ! -f "$cert_file" ]]; then
        print_error "Certificate file not found: $cert_file"
        return 1
    fi
    
    if [[ ! -f "$key_file" ]]; then
        print_error "Private key file not found: $key_file"
        return 1
    fi
    
    # Check certificate validity
    print_status "Checking certificate validity..."
    
    if openssl x509 -in "$cert_file" -text -noout > /dev/null 2>&1; then
        print_status "✅ Certificate is valid"
        
        # Show certificate details
        local expiry_date=$(openssl x509 -in "$cert_file" -noout -dates | grep notAfter | cut -d= -f2)
        local subject=$(openssl x509 -in "$cert_file" -noout -subject | cut -d= -f2-)
        
        print_status "Certificate Subject: $subject"
        print_status "Certificate Expires: $expiry_date"
    else
        print_error "Certificate is invalid"
        return 1
    fi
    
    # Check private key
    if openssl rsa -in "$key_file" -check -noout > /dev/null 2>&1; then
        print_status "✅ Private key is valid"
    else
        print_error "Private key is invalid"
        return 1
    fi
    
    # Check if certificate and key match
    local cert_md5=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5 | cut -d' ' -f2)
    local key_md5=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5 | cut -d' ' -f2)
    
    if [[ "$cert_md5" == "$key_md5" ]]; then
        print_status "✅ Certificate and private key match"
    else
        print_error "Certificate and private key do not match"
        return 1
    fi
    
    print_status "SSL certificate verification completed successfully!"
}

update_docker_compose() {
    print_step "Updating Docker Compose for SSL..."
    
    local ssl_override="$PROJECT_ROOT/docker-compose.ssl.yml"
    
    cat > "$ssl_override" << EOF
version: '3.8'

services:
  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    environment:
      - SSL_ENABLED=true
      - DOMAIN=$DOMAIN

  backend:
    environment:
      - DOMAIN=$DOMAIN
      - SSL_ENABLED=true

  frontend:
    environment:
      - VITE_API_BASE_URL=https://$DOMAIN/api/v1
      - VITE_WS_URL=wss://$DOMAIN/ws
EOF
    
    print_status "Docker Compose SSL override created: $ssl_override"
    
    # Update main docker-compose to include SSL
    local main_compose="$PROJECT_ROOT/docker-compose.yml"
    if [[ -f "$main_compose" ]]; then
        if ! grep -q "docker-compose.ssl.yml" "$main_compose"; then
            print_status "To use SSL, run: docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d"
        fi
    fi
}

create_ssl_scripts() {
    print_step "Creating SSL management scripts..."
    
    # SSL status script
    cat > "$PROJECT_ROOT/scripts/ssl-status.sh" << EOF
#!/bin/bash

# SSL Certificate Status Script

SSL_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)/nginx/ssl"
DOMAIN="$DOMAIN"

echo "🔒 SSL Certificate Status for \$DOMAIN"
echo "========================================"

if [[ -f "\$SSL_DIR/\$DOMAIN.crt" ]]; then
    echo "Certificate file: ✅ Found"
    
    # Check expiry
    expiry_date=\$(openssl x509 -in "\$SSL_DIR/\$DOMAIN.crt" -noout -dates | grep notAfter | cut -d= -f2)
    expiry_epoch=\$(date -d "\$expiry_date" +%s)
    current_epoch=\$(date +%s)
    days_until_expiry=\$(( (expiry_epoch - current_epoch) / 86400 ))
    
    echo "Expires: \$expiry_date"
    echo "Days until expiry: \$days_until_expiry"
    
    if [[ \$days_until_expiry -lt 30 ]]; then
        echo "⚠️  Certificate expires soon!"
    elif [[ \$days_until_expiry -lt 0 ]]; then
        echo "❌ Certificate has expired!"
    else
        echo "✅ Certificate is valid"
    fi
    
    # Check certificate details
    subject=\$(openssl x509 -in "\$SSL_DIR/\$DOMAIN.crt" -noout -subject | cut -d= -f2-)
    issuer=\$(openssl x509 -in "\$SSL_DIR/\$DOMAIN.crt" -noout -issuer | cut -d= -f2-)
    
    echo "Subject: \$subject"
    echo "Issuer: \$issuer"
else
    echo "Certificate file: ❌ Not found"
fi

if [[ -f "\$SSL_DIR/\$DOMAIN.key" ]]; then
    echo "Private key file: ✅ Found"
else
    echo "Private key file: ❌ Not found"
fi

echo
echo "🔧 SSL Management Commands:"
echo "  Renew certificate:    ./scripts/renew-ssl.sh"
echo "  Check nginx config:   docker-compose exec nginx nginx -t"
echo "  Restart nginx:        docker-compose restart nginx"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/ssl-status.sh"
    
    print_status "SSL management scripts created"
}

main() {
    echo "🔒 SSL Certificate Setup for Zmarty Dashboard"
    echo "============================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -t|--type)
                SSL_TYPE="$2"
                shift 2
                ;;
            -s|--staging)
                STAGING=true
                shift
                ;;
            -f|--force)
                FORCE_RENEW=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate required parameters
    if [[ -z "$DOMAIN" ]]; then
        print_error "Domain is required. Use -d or --domain option."
        show_help
        exit 1
    fi
    
    if ! validate_domain "$DOMAIN"; then
        exit 1
    fi
    
    if [[ "$SSL_TYPE" == "letsencrypt" && -n "$EMAIL" ]]; then
        if ! validate_email "$EMAIL"; then
            exit 1
        fi
    fi
    
    # Validate SSL type
    if [[ ! "$SSL_TYPE" =~ ^(letsencrypt|self-signed|custom)$ ]]; then
        print_error "Invalid SSL type: $SSL_TYPE"
        print_error "Valid types: letsencrypt, self-signed, custom"
        exit 1
    fi
    
    # Show configuration
    print_status "Configuration:"
    print_status "  Domain: $DOMAIN"
    print_status "  SSL Type: $SSL_TYPE"
    if [[ -n "$EMAIL" ]]; then
        print_status "  Email: $EMAIL"
    fi
    if [[ "$STAGING" == true ]]; then
        print_status "  Environment: Staging"
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Setup SSL based on type
    case $SSL_TYPE in
        letsencrypt)
            setup_letsencrypt
            ;;
        self-signed)
            setup_self_signed
            ;;
        custom)
            setup_custom
            ;;
    esac
    
    # Verify certificates
    if verify_certificates; then
        # Update configurations
        update_nginx_config
        update_docker_compose
        create_ssl_scripts
        
        print_status "🎉 SSL setup completed successfully!"
        echo
        echo "📋 Next steps:"
        echo "1. Start services with SSL: docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d"
        echo "2. Test your site: https://$DOMAIN"
        echo "3. Check SSL status: ./scripts/ssl-status.sh"
        echo
        
        if [[ "$SSL_TYPE" == "letsencrypt" ]]; then
            echo "🔄 Auto-renewal:"
            echo "  - Certificates will auto-renew daily at 12:00"
            echo "  - Manual renewal: ./scripts/renew-ssl.sh"
            echo
        fi
        
        if [[ "$SSL_TYPE" == "self-signed" ]]; then
            echo "⚠️  Development SSL Notes:"
            echo "  - Browsers will show security warnings"
            echo "  - Use only for development/testing"
            echo "  - For production, use Let's Encrypt certificates"
            echo
        fi
        
        echo "🔧 SSL Management:"
        echo "  Check status: ./scripts/ssl-status.sh"
        echo "  View config: cat nginx/nginx.conf"
        echo "  Test nginx: docker-compose exec nginx nginx -t"
        echo
    else
        print_error "SSL setup failed during verification"
        exit 1
    fi
}

# Run main function
main "$@"