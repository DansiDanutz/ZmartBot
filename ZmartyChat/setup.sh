#!/bin/bash

# ZmartyChat Setup Script
# This script sets up the complete ZmartyChat system

echo "🚀 ZmartyChat Setup Script"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Please run this script from the ZmartyChat root directory${NC}"
    exit 1
fi

# Step 1: Check Node.js version
echo "1️⃣  Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js 18+ required. Current version: $(node -v)${NC}"
    echo "Please install Node.js 18 or higher from https://nodejs.org"
    exit 1
else
    echo -e "${GREEN}✓ Node.js version: $(node -v)${NC}"
fi

# Step 2: Install dependencies
echo ""
echo "2️⃣  Installing dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}Error installing dependencies${NC}"
    exit 1
fi

# Step 3: Check for .env file
echo ""
echo "3️⃣  Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials${NC}"
    echo ""
    echo "Required configurations:"
    echo "  - Supabase URL and keys"
    echo "  - Stripe API keys"
    echo "  - Manus webhook URL"
    echo "  - ElevenLabs API key (optional)"
    echo ""
    read -p "Press Enter to open .env in your default editor..."
    ${EDITOR:-nano} .env
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Step 4: Validate required environment variables
echo ""
echo "4️⃣  Validating environment variables..."
source .env

MISSING_VARS=()
if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://your-project.supabase.co" ]; then
    MISSING_VARS+=("SUPABASE_URL")
fi
if [ -z "$SUPABASE_ANON_KEY" ] || [ "$SUPABASE_ANON_KEY" = "your-anon-key-here" ]; then
    MISSING_VARS+=("SUPABASE_ANON_KEY")
fi
if [ -z "$STRIPE_SECRET_KEY" ] || [ "$STRIPE_SECRET_KEY" = "sk_test_your_secret_key_here" ]; then
    MISSING_VARS+=("STRIPE_SECRET_KEY")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing or default environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please configure these in your .env file before proceeding."
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Environment variables configured${NC}"
fi

# Step 5: Setup Supabase
echo ""
echo "5️⃣  Setting up Supabase database..."
echo ""
echo "Please ensure you have:"
echo "1. Created a Supabase project at https://supabase.com"
echo "2. Copied the URL and anon key to .env"
echo ""
read -p "Have you completed Supabase setup? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running database migration..."

    # Check if psql is available
    if command -v psql &> /dev/null; then
        echo "Enter your Supabase database password:"
        read -s DB_PASSWORD

        # Extract host from Supabase URL
        SUPABASE_HOST=$(echo $SUPABASE_URL | sed 's|https://||' | sed 's|\.supabase\.co||')

        # Run migration
        PGPASSWORD=$DB_PASSWORD psql \
            -h db.${SUPABASE_HOST}.supabase.co \
            -p 5432 \
            -U postgres \
            -d postgres \
            -f database/supabase_schema.sql

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Database migration completed${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not run migration automatically${NC}"
            echo "Please run the following SQL in Supabase SQL Editor:"
            echo "  database/supabase_schema.sql"
        fi
    else
        echo -e "${YELLOW}⚠️  psql not found. Please run the migration manually:${NC}"
        echo "1. Go to your Supabase project SQL Editor"
        echo "2. Copy and run the contents of database/supabase_schema.sql"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping database setup${NC}"
fi

# Step 6: Setup Stripe
echo ""
echo "6️⃣  Setting up Stripe..."
echo ""
echo "Please ensure you have:"
echo "1. Created a Stripe account at https://stripe.com"
echo "2. Created products and price IDs for subscription tiers"
echo "3. Set up webhook endpoint: https://your-domain.com/api/stripe/webhook"
echo "4. Added webhook events: payment_intent.succeeded, customer.subscription.created, etc."
echo ""
read -p "Have you completed Stripe setup? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}✓ Stripe configuration confirmed${NC}"
else
    echo -e "${YELLOW}⚠️  Remember to configure Stripe before accepting payments${NC}"
fi

# Step 7: Check Manus connection
echo ""
echo "7️⃣  Checking Manus webhook connection..."
if [ ! -z "$MANUS_WEBHOOK_URL" ] && [ "$MANUS_WEBHOOK_URL" != "http://localhost:8000" ]; then
    curl -s -o /dev/null -w "%{http_code}" $MANUS_WEBHOOK_URL/health > /tmp/manus_check 2>/dev/null
    HTTP_STATUS=$(cat /tmp/manus_check)

    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ Manus webhook is reachable${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not reach Manus webhook at $MANUS_WEBHOOK_URL${NC}"
        echo "Make sure Manus is running before starting ZmartyChat"
    fi
else
    echo -e "${YELLOW}⚠️  Using default Manus URL. Update in .env if needed${NC}"
fi

# Step 8: Create necessary directories
echo ""
echo "8️⃣  Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp
echo -e "${GREEN}✓ Directories created${NC}"

# Step 9: Generate JWT secret if needed
echo ""
echo "9️⃣  Checking JWT secret..."
if [ "$JWT_SECRET" = "your-super-secret-jwt-key-change-this-in-production" ]; then
    NEW_SECRET=$(openssl rand -base64 32)
    sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$NEW_SECRET/" .env
    echo -e "${GREEN}✓ Generated new JWT secret${NC}"
else
    echo -e "${GREEN}✓ JWT secret configured${NC}"
fi

# Step 10: Final checks
echo ""
echo "🔟 Running final checks..."
echo ""

# Check if main files exist
FILES_TO_CHECK=(
    "src/main-integration.js"
    "src/supabase-client.js"
    "src/credit-manager.js"
    "src/zmarty-ai-agent.js"
    "database/supabase_schema.sql"
    "index.html"
)

ALL_FILES_EXIST=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file missing${NC}"
        ALL_FILES_EXIST=false
    fi
done

echo ""
echo "=================================="
echo ""

if [ "$ALL_FILES_EXIST" = true ]; then
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start the development server:"
    echo "   npm run dev"
    echo ""
    echo "2. Start background processor (in new terminal):"
    echo "   npm run background"
    echo ""
    echo "3. Start MCP servers (in new terminal):"
    echo "   npm run mcp:all"
    echo ""
    echo "4. Open the app:"
    echo "   http://localhost:8080"
    echo ""
    echo "5. For production deployment:"
    echo "   - Use a process manager like PM2"
    echo "   - Set up SSL certificates"
    echo "   - Configure domain and DNS"
    echo "   - Set NODE_ENV=production"
    echo ""

    read -p "Would you like to start the development server now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting ZmartyChat..."
        npm run dev
    fi
else
    echo -e "${RED}⚠️  Setup incomplete. Some files are missing.${NC}"
    echo "Please ensure all source files are present and run setup again."
    exit 1
fi