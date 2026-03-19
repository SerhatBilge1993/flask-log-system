import logging
import os

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider


def setup_otel_logging(service_name: str = "flask-app") -> None:
    base = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://192.168.8.247:4318").rstrip("/")

    provider = LoggerProvider(resource=Resource.create({"service.name": service_name}))
    set_logger_provider(provider)

    exporter = OTLPLogExporter(endpoint=f"{base}/v1/logs")
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    json_logger = logging.getLogger("json")
    json_logger.setLevel(logging.INFO)
    json_logger.addHandler(handler)    