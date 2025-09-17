"""
FastAPI Server - GptMDSagentService API
=======================================
RESTful API server for document processing operations
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import REGISTRY

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.gpt_foundation import GPTFoundation, GPTConfig, ModelType
from processors.mdc_processor import MDCMDSProcessor, DocumentType, ParsedDocument
from integrations.registry_client import ZmartBotIntegration

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('gpt_mds_requests_total', 'Total requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('gpt_mds_request_duration_seconds', 'Request duration', ['endpoint'])
GPT_CALLS = Counter('gpt_mds_gpt_calls_total', 'Total GPT API calls', ['model', 'status'])
DOCUMENT_PROCESSING = Counter('gpt_mds_document_processing_total', 'Document processing', ['operation', 'status'])

# Pydantic models for API
class DocumentRequest(BaseModel):
    content: str = Field(..., description="Document content to process")
    doc_type: str = Field(default="mdc", description="Document type (mdc/mds)")
    instructions: Optional[str] = Field(None, description="Processing instructions")

class DocumentGenerationRequest(BaseModel):
    description: str = Field(..., description="Service/component description")
    doc_type: str = Field(default="mdc", description="Document type to generate")
    service_type: str = Field(default="backend", description="Type of service")
    include_examples: bool = Field(default=True, description="Include code examples")

class DocumentEnhancementRequest(BaseModel):
    content: str = Field(..., description="Original document content")
    instructions: str = Field(default="", description="Enhancement instructions")
    preserve_original: bool = Field(default=True, description="Preserve original content")

class ValidationRequest(BaseModel):
    content: str = Field(..., description="Document content to validate")

class ServiceRegistrationRequest(BaseModel):
    service_name: str = Field(..., description="Name of the service")
    service_type: str = Field(default="backend", description="Type of service")
    description: str = Field(default="", description="Service description")
    health_url: Optional[str] = Field(None, description="Health check URL")
    dependencies: List[str] = Field(default_factory=list, description="Service dependencies")
    tags: List[str] = Field(default_factory=list, description="Service tags")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: float
    gpt_connection: bool
    registry_connection: bool
    metrics: Dict[str, Any]

class ProcessingResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class GptMDSagentServer:
    """
    FastAPI server for GptMDSagentService
    """
    
    def __init__(self, 
                 host: str = "0.0.0.0",
                 port: int = 8700,
                 openai_api_key: Optional[str] = None,
                 registry_url: str = "http://localhost:8610"):
        
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        
        # Initialize GPT foundation
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        gpt_config = GPTConfig(
            api_key=api_key,
            primary_model=ModelType.GPT_4O.value,
            fallback_model=ModelType.GPT_4O_MINI.value,
            temperature=0.1,
            max_tokens=4000,
            enable_cache=True
        )
        
        self.gpt_foundation = GPTFoundation(gpt_config)
        
        # Initialize processors
        self.mdc_processor = MDCMDSProcessor(self.gpt_foundation)
        
        # Initialize ZmartBot integration
        self.zmartbot_integration = ZmartBotIntegration(registry_url)
        
        # Create FastAPI app
        self.app = FastAPI(
            title="GptMDSagentService",
            description="GPT-powered MDC/MDS document processing and generation service",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Background tasks
        self.background_tasks = []
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            REQUEST_COUNT.labels(endpoint="/", method="GET").inc()
            return {
                "service": "GptMDSagentService",
                "version": "1.0.0",
                "status": "running",
                "docs": "/docs"
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
            
            # Check GPT connection
            gpt_healthy = await self.gpt_foundation.validate_connection()
            
            # Check registry connection
            registry_healthy = await self.zmartbot_integration.health_check()
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return HealthResponse(
                status="healthy" if gpt_healthy and registry_healthy else "degraded",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                uptime=uptime,
                gpt_connection=gpt_healthy,
                registry_connection=registry_healthy,
                metrics={
                    "gpt": self.gpt_foundation.get_metrics(),
                    "processor": self.mdc_processor.get_stats(),
                    "integration": self.zmartbot_integration.get_integration_stats()
                }
            )
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            REQUEST_COUNT.labels(endpoint="/metrics", method="GET").inc()
            return JSONResponse(
                content=generate_latest(REGISTRY),
                media_type=CONTENT_TYPE_LATEST
            )
        
        @self.app.post("/process", response_model=ProcessingResponse)
        async def process_document(request: DocumentRequest):
            """Process MDC/MDS document"""
            REQUEST_COUNT.labels(endpoint="/process", method="POST").inc()
            
            with REQUEST_DURATION.labels(endpoint="/process").time():
                try:
                    # Parse document
                    doc_type = DocumentType(request.doc_type.lower())
                    parsed_doc = self.mdc_processor.parse_document(request.content, doc_type)
                    
                    # Process with GPT if instructions provided
                    if request.instructions:
                        enhanced_content = await self.mdc_processor.enhance_document(
                            request.content,
                            request.instructions
                        )
                        content = enhanced_content
                    else:
                        content = request.content
                    
                    DOCUMENT_PROCESSING.labels(operation="process", status="success").inc()
                    
                    return ProcessingResponse(
                        success=True,
                        content=content,
                        metadata={
                            "doc_type": doc_type.value,
                            "title": parsed_doc.title,
                            "functions": len(parsed_doc.functions),
                            "steps": len(parsed_doc.steps),
                            "variables": len(parsed_doc.variables),
                            "hash": parsed_doc.hash
                        }
                    )
                    
                except Exception as e:
                    DOCUMENT_PROCESSING.labels(operation="process", status="error").inc()
                    logger.error("Document processing failed", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/generate", response_model=ProcessingResponse)
        async def generate_document(request: DocumentGenerationRequest):
            """Generate new MDC/MDS document"""
            REQUEST_COUNT.labels(endpoint="/generate", method="POST").inc()
            
            with REQUEST_DURATION.labels(endpoint="/generate").time():
                try:
                    doc_type = DocumentType(request.doc_type.lower())
                    
                    generated_content = await self.mdc_processor.generate_document(
                        request.description,
                        doc_type,
                        request.service_type,
                        request.include_examples
                    )
                    
                    DOCUMENT_PROCESSING.labels(operation="generate", status="success").inc()
                    
                    return ProcessingResponse(
                        success=True,
                        content=generated_content,
                        metadata={
                            "doc_type": doc_type.value,
                            "service_type": request.service_type,
                            "include_examples": request.include_examples,
                            "length": len(generated_content)
                        }
                    )
                    
                except Exception as e:
                    DOCUMENT_PROCESSING.labels(operation="generate", status="error").inc()
                    logger.error("Document generation failed", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/enhance", response_model=ProcessingResponse)
        async def enhance_document(request: DocumentEnhancementRequest):
            """Enhance existing MDC/MDS document"""
            REQUEST_COUNT.labels(endpoint="/enhance", method="POST").inc()
            
            with REQUEST_DURATION.labels(endpoint="/enhance").time():
                try:
                    enhanced_content = await self.mdc_processor.enhance_document(
                        request.content,
                        request.instructions,
                        request.preserve_original
                    )
                    
                    DOCUMENT_PROCESSING.labels(operation="enhance", status="success").inc()
                    
                    return ProcessingResponse(
                        success=True,
                        content=enhanced_content,
                        metadata={
                            "original_length": len(request.content),
                            "enhanced_length": len(enhanced_content),
                            "preserve_original": request.preserve_original
                        }
                    )
                    
                except Exception as e:
                    DOCUMENT_PROCESSING.labels(operation="enhance", status="error").inc()
                    logger.error("Document enhancement failed", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/validate", response_model=ProcessingResponse)
        async def validate_document(request: ValidationRequest):
            """Validate MDC/MDS document"""
            REQUEST_COUNT.labels(endpoint="/validate", method="POST").inc()
            
            with REQUEST_DURATION.labels(endpoint="/validate").time():
                try:
                    validation_results = await self.mdc_processor.validate_document(request.content)
                    
                    DOCUMENT_PROCESSING.labels(operation="validate", status="success").inc()
                    
                    return ProcessingResponse(
                        success=validation_results["valid"],
                        metadata={
                            "score": validation_results["score"],
                            "valid": validation_results["valid"]
                        },
                        errors=validation_results["errors"],
                        warnings=validation_results["warnings"]
                    )
                    
                except Exception as e:
                    DOCUMENT_PROCESSING.labels(operation="validate", status="error").inc()
                    logger.error("Document validation failed", error=str(e))
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/services", response_model=List[Dict[str, Any]])
        async def list_services():
            """List all ZmartBot services"""
            REQUEST_COUNT.labels(endpoint="/services", method="GET").inc()
            
            try:
                services = await self.zmartbot_integration.discover_services()
                return [service.__dict__ for service in services]
            except Exception as e:
                logger.error("Failed to list services", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/services/{service_name}", response_model=Dict[str, Any])
        async def get_service(service_name: str):
            """Get specific service details"""
            REQUEST_COUNT.labels(endpoint=f"/services/{service_name}", method="GET").inc()
            
            try:
                service = await self.zmartbot_integration.get_service_details(service_name)
                if service:
                    return service.__dict__
                else:
                    raise HTTPException(status_code=404, detail="Service not found")
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Failed to get service", name=service_name, error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/services/register", response_model=ProcessingResponse)
        async def register_service(request: ServiceRegistrationRequest):
            """Register new service with ZmartBot"""
            REQUEST_COUNT.labels(endpoint="/services/register", method="POST").inc()
            
            try:
                success, assigned_port = await self.zmartbot_integration.register_new_service(
                    request.service_name,
                    request.service_type,
                    request.description,
                    request.health_url,
                    request.dependencies,
                    request.tags
                )
                
                if success:
                    return ProcessingResponse(
                        success=True,
                        metadata={
                            "service_name": request.service_name,
                            "assigned_port": assigned_port,
                            "service_type": request.service_type
                        }
                    )
                else:
                    return ProcessingResponse(
                        success=False,
                        errors=["Failed to register service"]
                    )
                    
            except Exception as e:
                logger.error("Service registration failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/ports", response_model=List[Dict[str, Any]])
        async def list_ports():
            """List all port assignments"""
            REQUEST_COUNT.labels(endpoint="/ports", method="GET").inc()
            
            try:
                assignments = self.zmartbot_integration.get_port_assignments()
                return [assignment.__dict__ for assignment in assignments]
            except Exception as e:
                logger.error("Failed to list ports", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/gpt/models", response_model=List[str])
        async def list_gpt_models():
            """List available GPT models"""
            REQUEST_COUNT.labels(endpoint="/gpt/models", method="GET").inc()
            
            return [model.value for model in ModelType]
        
        @self.app.post("/gpt/test")
        async def test_gpt_connection():
            """Test GPT API connection"""
            REQUEST_COUNT.labels(endpoint="/gpt/test", method="POST").inc()
            
            try:
                is_healthy = await self.gpt_foundation.validate_connection()
                return {"connected": is_healthy}
            except Exception as e:
                logger.error("GPT connection test failed", error=str(e))
                return {"connected": False, "error": str(e)}
    
    async def start(self):
        """Start the server"""
        logger.info("Starting GptMDSagentService server",
                   host=self.host,
                   port=self.port)
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the server"""
        logger.info("Stopping GptMDSagentService server")
        
        # Cleanup background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Disconnect from ZmartBot
        await self.zmartbot_integration.registry_client.disconnect()

# Global server instance
server_instance: Optional[GptMDSagentServer] = None

def get_server() -> GptMDSagentServer:
    """Get server instance"""
    global server_instance
    if server_instance is None:
        raise RuntimeError("Server not initialized")
    return server_instance

async def create_server(host: str = "0.0.0.0",
                       port: int = 8700,
                       openai_api_key: Optional[str] = None,
                       registry_url: str = "http://localhost:8610") -> GptMDSagentServer:
    """Create and configure server instance"""
    global server_instance
    
    server_instance = GptMDSagentServer(
        host=host,
        port=port,
        openai_api_key=openai_api_key,
        registry_url=registry_url
    )
    
    return server_instance
