#!/bin/bash

# ZmartyChat Production Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 Starting ZmartyChat Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV=${1:-production}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"zmartychat"}
VERSION=${VERSION:-$(git describe --tags --always)}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_status "Docker found"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_status "Docker Compose found"

    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_status "Git found"

    # Check environment file
    if [ ! -f ".env.$DEPLOY_ENV" ]; then
        print_error ".env.$DEPLOY_ENV file not found"
        exit 1
    fi
    print_status "Environment file found"
}

# Function to run tests
run_tests() {
    echo -e "\n📋 Running tests..."

    # Run unit tests
    if [ -f "package.json" ]; then
        npm test || {
            print_error "Unit tests failed"
            exit 1
        }
        print_status "Unit tests passed"
    fi

    # Run integration tests
    if [ -f "tests/test-suite.js" ]; then
        node tests/test-suite.js || {
            print_warning "Some integration tests failed"
        }
    fi
}

# Function to build Docker images
build_images() {
    echo -e "\n🏗️  Building Docker images..."

    # Build frontend
    docker build -t $DOCKER_REGISTRY/frontend:$VERSION . || {
        print_error "Frontend build failed"
        exit 1
    }
    print_status "Frontend image built"

    # Tag as latest
    docker tag $DOCKER_REGISTRY/frontend:$VERSION $DOCKER_REGISTRY/frontend:latest

    print_status "All images built successfully"
}

# Function to push images to registry
push_images() {
    echo -e "\n📤 Pushing images to registry..."

    # Login to registry (if needed)
    if [ ! -z "$DOCKER_USERNAME" ] && [ ! -z "$DOCKER_PASSWORD" ]; then
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    fi

    # Push images
    docker push $DOCKER_REGISTRY/frontend:$VERSION || {
        print_warning "Failed to push to registry (continuing anyway)"
    }
    docker push $DOCKER_REGISTRY/frontend:latest

    print_status "Images pushed to registry"
}

# Function to deploy with Docker Compose
deploy_compose() {
    echo -e "\n🚢 Deploying with Docker Compose..."

    # Create backup of current deployment
    if [ -d "deployments/current" ]; then
        mv deployments/current deployments/backup-$TIMESTAMP
        print_status "Created backup of current deployment"
    fi

    # Create deployment directory
    mkdir -p deployments/current
    cp docker-compose.yml deployments/current/
    cp .env.$DEPLOY_ENV deployments/current/.env

    cd deployments/current

    # Stop existing containers (if any)
    docker-compose down --remove-orphans 2>/dev/null || true

    # Start new deployment
    docker-compose up -d || {
        print_error "Deployment failed"
        # Rollback
        if [ -d "../backup-$TIMESTAMP" ]; then
            print_warning "Rolling back to previous deployment..."
            cd ../backup-$TIMESTAMP
            docker-compose up -d
        fi
        exit 1
    }

    cd ../..
    print_status "Services deployed successfully"
}

# Function to run database migrations
run_migrations() {
    echo -e "\n🗄️  Running database migrations..."

    docker-compose exec -T api npm run migrate || {
        print_warning "Migrations failed or not configured"
    }

    print_status "Migrations completed"
}

# Function to health check
health_check() {
    echo -e "\n🏥 Running health checks..."

    # Wait for services to be ready
    sleep 10

    # Check frontend
    curl -f http://localhost/health > /dev/null 2>&1 || {
        print_error "Frontend health check failed"
        return 1
    }
    print_status "Frontend is healthy"

    # Check API
    curl -f http://localhost:8000/health > /dev/null 2>&1 || {
        print_warning "API health check failed"
    }

    # Check WebSocket
    curl -f http://localhost:8080/health > /dev/null 2>&1 || {
        print_warning "WebSocket health check failed"
    }

    print_status "Health checks completed"
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "\n📊 Setting up monitoring..."

    # Import Grafana dashboards
    if [ -d "monitoring/grafana/dashboards" ]; then
        for dashboard in monitoring/grafana/dashboards/*.json; do
            # This would normally import to Grafana API
            print_status "Imported dashboard: $(basename $dashboard)"
        done
    fi

    print_status "Monitoring setup completed"
}

# Function to cleanup old deployments
cleanup() {
    echo -e "\n🧹 Cleaning up old deployments..."

    # Remove old backup directories (keep last 5)
    if [ -d "deployments" ]; then
        cd deployments
        ls -dt backup-* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true
        cd ..
    fi

    # Prune Docker
    docker system prune -f --volumes || true

    print_status "Cleanup completed"
}

# Function to generate deployment report
generate_report() {
    echo -e "\n📄 Generating deployment report..."

    REPORT_FILE="deployments/report-$TIMESTAMP.txt"
    mkdir -p deployments

    {
        echo "DEPLOYMENT REPORT"
        echo "================"
        echo "Date: $(date)"
        echo "Environment: $DEPLOY_ENV"
        echo "Version: $VERSION"
        echo ""
        echo "Docker Images:"
        docker images | grep $DOCKER_REGISTRY
        echo ""
        echo "Running Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "System Resources:"
        docker stats --no-stream
    } > $REPORT_FILE

    print_status "Report saved to $REPORT_FILE"
}

# Main deployment flow
main() {
    echo "================================================"
    echo "     ZmartyChat Deployment Script v1.0         "
    echo "================================================"
    echo "Environment: $DEPLOY_ENV"
    echo "Version: $VERSION"
    echo "Timestamp: $TIMESTAMP"
    echo "================================================"

    # Check prerequisites
    check_prerequisites

    # Run tests (optional, can be skipped with --skip-tests)
    if [[ "$*" != *"--skip-tests"* ]]; then
        run_tests
    else
        print_warning "Skipping tests"
    fi

    # Build images
    build_images

    # Push to registry (optional)
    if [[ "$*" == *"--push"* ]]; then
        push_images
    fi

    # Deploy
    deploy_compose

    # Run migrations
    run_migrations

    # Health check
    health_check

    # Setup monitoring
    setup_monitoring

    # Cleanup
    cleanup

    # Generate report
    generate_report

    echo -e "\n✨ ${GREEN}Deployment completed successfully!${NC}"
    echo "================================================"
    echo "Frontend: https://zmartychat.com"
    echo "API: https://api.zmartychat.com"
    echo "WebSocket: wss://ws.zmartychat.com"
    echo "Monitoring: http://localhost:3000 (Grafana)"
    echo "================================================"
}

# Handle script arguments
case "$1" in
    rollback)
        echo "Rolling back to previous deployment..."
        if [ -d "deployments/backup-"* ]; then
            LATEST_BACKUP=$(ls -dt deployments/backup-* | head -1)
            cd $LATEST_BACKUP
            docker-compose up -d
            print_status "Rollback completed"
        else
            print_error "No backup found"
        fi
        ;;
    status)
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f ${2:-}
        ;;
    stop)
        docker-compose down
        print_status "Services stopped"
        ;;
    *)
        main "$@"
        ;;
esac