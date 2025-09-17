from ..config import settings
from loguru import logger
def setup_otel(app):
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
            provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            FastAPIInstrumentor.instrument_app(app)
            logger.info("OpenTelemetry → {}", settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        except Exception as e:
            logger.warning(f"OTel setup failed: {e}")
    else:
        logger.info("OpenTelemetry disabled")
