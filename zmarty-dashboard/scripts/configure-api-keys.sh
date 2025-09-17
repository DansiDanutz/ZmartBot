#!/bin/bash

# Zmarty Dashboard API Key Configuration Script
# This script helps you securely configure all necessary API keys

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
    echo -e "${PURPLE}    🔑 ZMARTY DASHBOARD API KEY SETUP    ${NC}"
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

# Function to read input with default value
read_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        eval $var_name="\${input:-$default}"
    else
        read -p "$prompt: " input
        eval $var_name="$input"
    fi
}

# Function to read sensitive input
read_secret() {
    local prompt="$1"
    local var_name="$2"
    
    echo -n "$prompt: "
    read -s input
    echo ""
    eval $var_name="$input"
}

# Function to validate API key format
validate_openai_key() {
    local key="$1"
    if [[ $key =~ ^sk-[a-zA-Z0-9]{48,}$ ]]; then
        return 0
    else
        return 1
    fi
}

validate_stripe_key() {
    local key="$1"
    local key_type="$2"
    
    case $key_type in
        "secret")
            if [[ $key =~ ^sk_(test_|live_)[a-zA-Z0-9]{24,}$ ]]; then
                return 0
            fi
            ;;
        "publishable")
            if [[ $key =~ ^pk_(test_|live_)[a-zA-Z0-9]{24,}$ ]]; then
                return 0
            fi
            ;;
        "webhook")
            if [[ $key =~ ^whsec_[a-zA-Z0-9]+$ ]]; then
                return 0
            fi
            ;;
    esac
    return 1
}

# Function to generate random secret key
generate_secret_key() {
    openssl rand -hex 32
}

# Function to test API key
test_openai_key() {
    local api_key="$1"
    
    print_info "Testing OpenAI API key..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/openai_test.json \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}],"max_tokens":5}' \
        https://api.openai.com/v1/chat/completions)
    
    if [[ $response == "200" ]]; then
        print_success "OpenAI API key is valid and working"
        return 0
    else
        print_error "OpenAI API key test failed (HTTP $response)"
        if [ -f "/tmp/openai_test.json" ]; then
            echo "Response: $(cat /tmp/openai_test.json)"
        fi
        return 1
    fi
}

# Function to test Stripe key
test_stripe_key() {
    local api_key="$1"
    
    print_info "Testing Stripe API key..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/stripe_test.json \
        -u "$api_key:" \
        https://api.stripe.com/v1/account)
    
    if [[ $response == "200" ]]; then
        print_success "Stripe API key is valid and working"
        return 0
    else
        print_error "Stripe API key test failed (HTTP $response)"
        if [ -f "/tmp/stripe_test.json" ]; then
            echo "Response: $(cat /tmp/stripe_test.json)"
        fi
        return 1
    fi
}

# Function to backup existing env files
backup_env_files() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    if [ -f "backend/.env" ]; then
        cp "backend/.env" "backend/.env.backup_$timestamp"
        print_info "Backed up backend/.env to backend/.env.backup_$timestamp"
    fi
    
    if [ -f "frontend/.env.local" ]; then
        cp "frontend/.env.local" "frontend/.env.local.backup_$timestamp"
        print_info "Backed up frontend/.env.local to frontend/.env.local.backup_$timestamp"
    fi
    
    if [ -f ".env" ]; then
        cp ".env" ".env.backup_$timestamp"
        print_info "Backed up .env to .env.backup_$timestamp"
    fi
}

# Main configuration function
main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the Zmarty Dashboard root directory"
        exit 1
    fi
    
    print_info "This script will help you configure all necessary API keys for your Zmarty Dashboard"
    echo ""
    
    # Ask for confirmation
    read -p "Do you want to continue? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Configuration cancelled."
        exit 0
    fi
    
    # Backup existing files
    print_step "Backing up existing configuration files..."
    backup_env_files
    
    echo ""
    print_step "1. OpenAI Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "You need an OpenAI API key for Zmarty AI functionality."
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    
    while true; do
        read_secret "Enter your OpenAI API key (sk-...)" OPENAI_API_KEY
        
        if [ -z "$OPENAI_API_KEY" ]; then
            print_warning "OpenAI API key is required for Zmarty functionality"
            continue
        fi
        
        if validate_openai_key "$OPENAI_API_KEY"; then
            # Test the key
            if test_openai_key "$OPENAI_API_KEY"; then
                break
            else
                print_warning "API key validation failed. Please check your key."
                read -p "Continue anyway? (y/N): " continue_anyway
                if [[ $continue_anyway =~ ^[Yy]$ ]]; then
                    break
                fi
            fi
        else
            print_error "Invalid OpenAI API key format"
            continue
        fi
    done
    
    # OpenAI Model Selection
    echo ""
    print_info "Select OpenAI model for Zmarty:"
    echo "1. gpt-3.5-turbo (Faster, cheaper)"
    echo "2. gpt-4-turbo-preview (Better quality, more expensive)"
    echo "3. gpt-4 (Best quality, most expensive)"
    
    read_with_default "Choose model (1-3)" "2" model_choice
    
    case $model_choice in
        1) OPENAI_MODEL="gpt-3.5-turbo" ;;
        2) OPENAI_MODEL="gpt-4-turbo-preview" ;;
        3) OPENAI_MODEL="gpt-4" ;;
        *) OPENAI_MODEL="gpt-4-turbo-preview" ;;
    esac
    
    print_success "OpenAI configured: $OPENAI_MODEL"
    
    echo ""
    echo ""
    print_step "2. Stripe Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "You need Stripe API keys for payment processing."
    echo "Get your API keys from: https://dashboard.stripe.com/apikeys"
    echo ""
    
    # Stripe Secret Key
    while true; do
        read_secret "Enter your Stripe Secret Key (sk_test_... or sk_live_...)" STRIPE_SECRET_KEY
        
        if [ -z "$STRIPE_SECRET_KEY" ]; then
            print_warning "Stripe secret key is required for payment processing"
            continue
        fi
        
        if validate_stripe_key "$STRIPE_SECRET_KEY" "secret"; then
            # Test the key
            if test_stripe_key "$STRIPE_SECRET_KEY"; then
                break
            else
                print_warning "Stripe key validation failed. Please check your key."
                read -p "Continue anyway? (y/N): " continue_anyway
                if [[ $continue_anyway =~ ^[Yy]$ ]]; then
                    break
                fi
            fi
        else
            print_error "Invalid Stripe secret key format"
            continue
        fi
    done
    
    # Stripe Publishable Key
    while true; do
        read -p "Enter your Stripe Publishable Key (pk_test_... or pk_live_...): " STRIPE_PUBLISHABLE_KEY
        
        if [ -z "$STRIPE_PUBLISHABLE_KEY" ]; then
            print_warning "Stripe publishable key is required"
            continue
        fi
        
        if validate_stripe_key "$STRIPE_PUBLISHABLE_KEY" "publishable"; then
            break
        else
            print_error "Invalid Stripe publishable key format"
            continue
        fi
    done
    
    # Stripe Webhook Secret
    echo ""
    print_info "Stripe Webhook Secret (optional but recommended):"
    echo "Create a webhook endpoint at: https://dashboard.stripe.com/webhooks"
    echo "Endpoint URL: https://yourdomain.com/api/v1/credits/webhook"
    
    read -p "Enter your Stripe Webhook Secret (whsec_...) [optional]: " STRIPE_WEBHOOK_SECRET
    
    if [ -n "$STRIPE_WEBHOOK_SECRET" ] && ! validate_stripe_key "$STRIPE_WEBHOOK_SECRET" "webhook"; then
        print_warning "Invalid webhook secret format, but continuing..."
    fi
    
    print_success "Stripe configuration completed"
    
    echo ""
    echo ""
    print_step "3. Security Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # JWT Secret Key
    read -p "Generate new JWT secret key? (Y/n): " generate_jwt
    if [[ ! $generate_jwt =~ ^[Nn]$ ]]; then
        JWT_SECRET_KEY=$(generate_secret_key)
        print_success "Generated new JWT secret key"
    else
        read_secret "Enter custom JWT secret key" JWT_SECRET_KEY
    fi
    
    # Database passwords
    read_with_default "PostgreSQL password" "postgres" POSTGRES_PASSWORD
    read_with_default "Redis password" "redis_password" REDIS_PASSWORD
    
    echo ""
    echo ""
    print_step "4. Optional Integrations"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Figma Token for MCP
    read -p "Enable Figma MCP integration? (y/N): " enable_figma
    if [[ $enable_figma =~ ^[Yy]$ ]]; then
        echo "Get your Figma token from: https://www.figma.com/developers/api#access-tokens"
        read -p "Enter your Figma Personal Access Token: " FIGMA_TOKEN
        ENABLE_MCP="true"
    else
        FIGMA_TOKEN=""
        ENABLE_MCP="false"
    fi
    
    # Email Configuration (optional)
    read -p "Configure email notifications? (y/N): " setup_email
    if [[ $setup_email =~ ^[Yy]$ ]]; then
        read_with_default "SMTP Host" "smtp.gmail.com" SMTP_HOST
        read_with_default "SMTP Port" "587" SMTP_PORT
        read -p "SMTP Username (email): " SMTP_USERNAME
        read_secret "SMTP Password (app password)" SMTP_PASSWORD
        read_with_default "From Email" "noreply@zmartydashboard.com" EMAIL_FROM
    else
        SMTP_HOST=""
        SMTP_PORT=""
        SMTP_USERNAME=""
        SMTP_PASSWORD=""
        EMAIL_FROM=""
    fi
    
    echo ""
    echo ""
    print_step "5. Writing Configuration Files"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Write backend .env
    print_info "Writing backend/.env..."
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5432/zmarty_dashboard

# JWT Authentication
SECRET_KEY=${JWT_SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Zmarty Dashboard API
VERSION=1.0.0

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

# Redis Configuration
REDIS_URL=redis://:${REDIS_PASSWORD}@localhost:6379/0

# OpenAI Configuration
ZMARTY_API_KEY=${OPENAI_API_KEY}
ZMARTY_MODEL=${OPENAI_MODEL}
ZMARTY_MAX_TOKENS=4000

# Stripe Payment Configuration
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}

# Email Configuration
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
EMAIL_FROM=${EMAIL_FROM}

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS_PER_USER=3

# MCP Configuration
MCP_FIGMA_SERVER_URL=http://localhost:3001
MCP_FIGMA_TIMEOUT=30

# Environment
ENVIRONMENT=development

# Security
TRUSTED_HOSTS=localhost,127.0.0.1,*.zmartydashboard.com

# Generated on: $(date)
EOF
    
    # Write frontend .env.local
    print_info "Writing frontend/.env.local..."
    cat > frontend/.env.local << EOF
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Stripe Configuration
VITE_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}

# MCP Configuration
VITE_MCP_ENABLED=${ENABLE_MCP}
VITE_MCP_SERVER_URL=http://localhost:3001

# Application Configuration
VITE_APP_NAME=Zmarty Dashboard
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=AI-Powered Cryptocurrency Trading Dashboard

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_CHAT_HISTORY=true
VITE_ENABLE_PERFORMANCE_METRICS=true

# UI Configuration
VITE_DEFAULT_THEME=light
VITE_DEFAULT_LANGUAGE=en
VITE_ENABLE_THEME_SWITCHING=true

# Generated on: $(date)
EOF
    
    # Write root .env for Docker Compose
    print_info "Writing .env for Docker Compose..."
    cat > .env << EOF
# Docker Compose Environment Variables
ZMARTY_API_KEY=${OPENAI_API_KEY}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
VITE_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
FIGMA_TOKEN=${FIGMA_TOKEN}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Generated on: $(date)
EOF
    
    print_success "Configuration files written successfully!"
    
    echo ""
    echo ""
    print_step "6. Configuration Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "✅ OpenAI API Key: Configured (${OPENAI_MODEL})"
    echo "✅ Stripe Secret Key: Configured"
    echo "✅ Stripe Publishable Key: Configured"
    
    if [ -n "$STRIPE_WEBHOOK_SECRET" ]; then
        echo "✅ Stripe Webhook Secret: Configured"
    else
        echo "⚠️  Stripe Webhook Secret: Not configured (optional)"
    fi
    
    echo "✅ JWT Secret Key: Generated"
    echo "✅ Database Credentials: Configured"
    
    if [[ $ENABLE_MCP == "true" ]]; then
        echo "✅ Figma MCP Integration: Enabled"
    else
        echo "⚠️  Figma MCP Integration: Disabled"
    fi
    
    if [ -n "$SMTP_USERNAME" ]; then
        echo "✅ Email Notifications: Configured"
    else
        echo "⚠️  Email Notifications: Not configured (optional)"
    fi
    
    echo ""
    print_success "🎉 API Key configuration completed successfully!"
    echo ""
    print_info "Next steps:"
    echo "1. Review the generated .env files"
    echo "2. Start the application: ./start.sh"
    echo "3. Visit: http://localhost:3000"
    echo ""
    print_warning "Keep your API keys secure and never commit them to version control!"
    
    # Clean up temp files
    rm -f /tmp/openai_test.json /tmp/stripe_test.json
}

# Run main function
main "$@"