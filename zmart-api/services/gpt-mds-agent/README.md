# GptMDSagentService

GPT-powered MDC/MDS document processing and generation service for the ZmartBot ecosystem.

## Overview

GptMDSagentService is the foundational AI infrastructure that powers intelligent documentation across ZmartBot. It processes MDC (Markdown Component) and MDS (Markdown Service) documents using OpenAI's GPT models, providing automated service documentation, code analysis, and system integration intelligence.

## Features

- **Advanced GPT Integration**: Multi-model support with intelligent model selection
- **MDC/MDS Processing**: Parse, validate, generate, and enhance documents
- **ZmartBot Integration**: Seamless connection to service registry and port management
- **RESTful API**: Comprehensive API for document operations
- **Monitoring & Metrics**: Prometheus metrics and structured logging
- **Caching**: Intelligent caching for improved performance
- **Error Handling**: Robust error handling with fallback mechanisms

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- ZmartBot ecosystem (optional, for full integration)

### Installation

1. Clone the repository:
```bash
cd services/gpt-mds-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. Run the service:
```bash
python src/main.py
```

### Configuration

The service can be configured via environment variables or command-line arguments:

```bash
python src/main.py \
  --host 0.0.0.0 \
  --port 8700 \
  --openai-api-key your-key \
  --registry-url http://localhost:8610 \
  --log-level INFO
```

## API Endpoints

### Health & Monitoring

- `GET /` - Service information
- `GET /health` - Health check with detailed metrics
- `GET /metrics` - Prometheus metrics

### Document Processing

- `POST /process` - Process MDC/MDS documents
- `POST /generate` - Generate new documents from descriptions
- `POST /enhance` - Enhance existing documents
- `POST /validate` - Validate document structure

### ZmartBot Integration

- `GET /services` - List all ZmartBot services
- `GET /services/{name}` - Get specific service details
- `POST /services/register` - Register new service
- `GET /ports` - List port assignments

### GPT Management

- `GET /gpt/models` - List available GPT models
- `POST /gpt/test` - Test GPT API connection

## Usage Examples

### Process a Document

```bash
curl -X POST http://localhost:8700/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# My Service\n\n## Overview\nThis is a test service.",
    "doc_type": "mdc",
    "instructions": "Add error handling section"
  }'
```

### Generate a New Document

```bash
curl -X POST http://localhost:8700/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A microservice for user authentication",
    "doc_type": "mdc",
    "service_type": "backend",
    "include_examples": true
  }'
```

### Register a Service

```bash
curl -X POST http://localhost:8700/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "auth-service",
    "service_type": "backend",
    "description": "User authentication service",
    "dependencies": ["database", "redis"],
    "tags": ["auth", "security"]
  }'
```

## Architecture

### Core Components

1. **GPT Foundation** (`core/gpt_foundation.py`)
   - OpenAI API integration
   - Model selection and caching
   - Rate limiting and error handling

2. **MDC/MDS Processor** (`processors/mdc_processor.py`)
   - Document parsing and validation
   - GPT-enhanced generation
   - Template rendering

3. **Registry Client** (`integrations/registry_client.py`)
   - ZmartBot service registry integration
   - Port management
   - Service discovery

4. **API Server** (`api/server.py`)
   - FastAPI-based REST server
   - Prometheus metrics
   - Health monitoring

### Data Flow

```
Client Request → API Server → GPT Foundation → MDC Processor → Response
                ↓
            Registry Client → ZmartBot Ecosystem
```

## Development

### Project Structure

```
services/gpt-mds-agent/
├── src/
│   ├── core/           # GPT foundation
│   ├── processors/     # Document processing
│   ├── integrations/   # ZmartBot integration
│   ├── api/           # REST API
│   └── utils/         # Utilities
├── tests/             # Test suite
├── config/            # Configuration files
├── templates/         # Jinja2 templates
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── logs/             # Log files
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_gpt_foundation.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Monitoring

### Metrics

The service exposes Prometheus metrics at `/metrics`:

- `gpt_mds_requests_total` - Total API requests
- `gpt_mds_request_duration_seconds` - Request duration
- `gpt_mds_gpt_calls_total` - GPT API calls
- `gpt_mds_document_processing_total` - Document processing operations

### Logging

Structured logging with JSON format:

```json
{
  "timestamp": "2025-08-28T10:30:00Z",
  "level": "info",
  "logger": "gpt_mds_agent",
  "message": "Document processed",
  "doc_type": "mdc",
  "functions": 3,
  "steps": 2
}
```

## Deployment

### Docker

```bash
# Build image
docker build -t gpt-mds-agent .

# Run container
docker run -p 8700:8700 \
  -e OPENAI_API_KEY=your-key \
  gpt-mds-agent
```

### Docker Compose

```yaml
version: '3.8'
services:
  gpt-mds-agent:
    build: .
    ports:
      - "8700:8700"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpt-mds-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gpt-mds-agent
  template:
    metadata:
      labels:
        app: gpt-mds-agent
    spec:
      containers:
      - name: gpt-mds-agent
        image: gpt-mds-agent:latest
        ports:
        - containerPort: 8700
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   ```
   Error: OpenAI API key is required
   ```
   Solution: Set `OPENAI_API_KEY` environment variable

2. **Registry Connection Failed**
   ```
   Error: Registry health check failed
   ```
   Solution: Ensure ZmartBot service registry is running

3. **Port Already in Use**
   ```
   Error: Address already in use
   ```
   Solution: Change port with `--port` argument

### Debug Mode

Enable debug logging:

```bash
python src/main.py --log-level DEBUG
```

### Health Check

Check service health:

```bash
curl http://localhost:8700/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the ZmartBot ecosystem and follows the same licensing terms.

## Support

For support and questions:

- Check the documentation
- Review the logs
- Open an issue on GitHub
- Contact the ZmartBot development team
