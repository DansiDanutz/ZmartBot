# Registration Service

Enterprise-grade service registration and management system for ZmartBot ecosystem, managing service registration lifecycle, validation, certification workflows, and comprehensive registration analytics with advanced visualization dashboards.

## Overview

The Registration Service is a critical component of the ZmartBot ecosystem that manages the complete lifecycle of service registration, from initial discovery through certification and ongoing management. It provides a centralized system for tracking all registered services, their status, and certification workflows.

## Features

### Core Capabilities
- **Service Registration Management**: Complete registration workflow from discovery to certification
- **Registration Validation**: Comprehensive validation of service requirements and dependencies
- **Certification Workflow**: Automated certification process with status tracking
- **Event Tracking**: Complete audit trail of all registration events
- **Analytics & Reporting**: Real-time analytics and performance metrics
- **Dashboard Management**: Interactive dashboards for registration management

### API Endpoints
- `GET /health` - Service health check
- `GET /ready` - Service readiness check
- `GET /api/registrations` - Get all service registrations
- `GET /api/registrations/{service_name}` - Get specific registration
- `POST /api/registrations` - Register a new service
- `PUT /api/registrations/{service_name}/certify` - Certify a service
- `GET /api/system/overview` - System overview and statistics
- `GET /api/analytics/registration-stats` - Registration analytics
- `GET /dashboard` - Interactive dashboard

## Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- SQLite3

### Installation
```bash
# Navigate to service directory
cd services/registration-service

# Install dependencies (if needed)
pip install fastapi uvicorn psutil

# Start the service
./start_registration_service.sh start
```

### Usage

#### Start the Service
```bash
./start_registration_service.sh start
```

#### Stop the Service
```bash
./start_registration_service.sh stop
```

#### Check Status
```bash
./start_registration_service.sh status
```

#### View Logs
```bash
./start_registration_service.sh logs
```

#### Restart the Service
```bash
./start_registration_service.sh restart
```

## API Usage

### Register a New Service
```bash
curl -X POST "http://localhost:8902/api/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "my-service",
    "service_type": "backend",
    "port": 8000,
    "passport_id": "ZMBT-SRV-20250829-ABC123",
    "description": "My new service",
    "metadata": {"version": "1.0.0"}
  }'
```

### Get All Registrations
```bash
curl "http://localhost:8902/api/registrations"
```

### Certify a Service
```bash
curl -X PUT "http://localhost:8902/api/registrations/my-service/certify"
```

### Get System Overview
```bash
curl "http://localhost:8902/api/system/overview"
```

## Dashboard

Access the interactive dashboard at: http://localhost:8902/dashboard

The dashboard provides:
- Real-time registration statistics
- Service type distribution
- Registration trends
- Recent registration events
- Certification status overview

## Database Schema

### registration_registry
- `id` - Primary key
- `service_name` - Unique service name
- `service_type` - Service type (backend, frontend, etc.)
- `port` - Assigned port
- `passport_id` - Passport ID
- `registration_status` - Registration status
- `registration_date` - Registration timestamp
- `certification_status` - Certification status
- `certification_date` - Certification timestamp
- `health_status` - Health status
- `last_health_check` - Last health check
- `metadata` - JSON metadata
- `description` - Service description
- `created_by` - Creator
- `updated_at` - Last update

### registration_events
- `id` - Primary key
- `service_name` - Service name
- `event_type` - Event type
- `event_data` - JSON event data
- `timestamp` - Event timestamp
- `created_by` - Creator

### registration_analytics
- `id` - Primary key
- `metric_name` - Metric name
- `metric_value` - Metric value
- `metric_date` - Metric date
- `service_name` - Service name
- `metadata` - JSON metadata
- `created_at` - Creation timestamp

## Configuration

### Environment Variables
- `REGISTRATION_SERVICE_PORT` - Service port (default: 8902)
- `REGISTRATION_DB_PATH` - Database path (default: data/registration_registry.db)

### Service Configuration
The service configuration is defined in `service.yaml` and includes:
- Service metadata
- API endpoints
- Dependencies
- Monitoring settings
- Security configuration

## Integration

### ZmartBot Ecosystem Integration
The Registration Service integrates with:
- **Passport Service**: For passport ID management
- **Certification Service**: For certification workflows
- **Port Manager**: For port assignment tracking
- **Master Orchestration Agent**: For system integration
- **Service Discovery**: For new service detection

### Workflow Integration
1. **Service Discovery**: New services are detected
2. **Registration**: Services are registered with metadata
3. **Validation**: Service requirements are validated
4. **Port Assignment**: Ports are assigned and tracked
5. **Passport Assignment**: Passport IDs are assigned
6. **Certification**: Services are certified
7. **Monitoring**: Ongoing monitoring and analytics

## Development

### File Structure
```
registration-service/
├── registration_service.py              # Main service implementation
├── registration_service.mdc             # MDC documentation
├── service.yaml                         # Service configuration
├── README.md                            # This file
├── start_registration_service.sh        # Startup script
├── data/                                # Database directory
│   └── registration_registry.db         # Registration database
└── registration_service.log             # Service logs
```

### Adding New Features
1. Update the service implementation in `registration_service.py`
2. Add new API endpoints as needed
3. Update the database schema if required
4. Update the MDC documentation
5. Test the changes
6. Update this README

## Monitoring

### Health Checks
- **Liveness**: `GET /health`
- **Readiness**: `GET /ready`
- **Metrics**: `GET /api/system/overview`

### Logs
Service logs are written to `registration_service.log` and include:
- Service startup/shutdown events
- API request logs
- Error messages
- Performance metrics

### Metrics
The service provides various metrics:
- Total registrations
- Certified services count
- Registration trends
- Service type distribution
- Event tracking

## Troubleshooting

### Common Issues

#### Service Won't Start
1. Check if port 8902 is available
2. Verify Python dependencies are installed
3. Check the log file for errors
4. Ensure the data directory is writable

#### Database Issues
1. Check database file permissions
2. Verify SQLite is available
3. Check database schema integrity

#### API Issues
1. Verify service is running
2. Check health endpoint
3. Review API documentation
4. Check request format

### Debug Mode
To run in debug mode:
```bash
python3 registration_service.py --port 8902 --debug
```

## Security

### Security Features
- Input validation on all endpoints
- CORS configuration
- Audit logging
- Error handling without information disclosure

### Best Practices
- Use HTTPS in production
- Implement authentication if needed
- Regular security updates
- Monitor access logs

## License

This service is part of the ZmartBot ecosystem and follows the same licensing terms.

## Support

For support and questions:
1. Check the logs for error messages
2. Review the API documentation
3. Check the dashboard for system status
4. Contact the ZmartBot development team
