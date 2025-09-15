import logging
from google.cloud import monitoring_v3
from google.cloud import logging as cloud_logging
from .gcp_auth import get_project_id
import time

logger = logging.getLogger(__name__)

class GCPTelemetry:
    def __init__(self):
        self.project_id = get_project_id()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
        # Initialize Cloud Logging
        logging_client = cloud_logging.Client()
        logging_client.setup_logging()
        
        logger.info("GCP telemetry initialized")
    
    def log_event(self, message: str, severity: str = "INFO"):
        """Log event to Cloud Logging"""
        try:
            # Cloud Logging automatically captures structured logs
            if severity == "ERROR":
                logger.error(message)
            elif severity == "WARNING":
                logger.warning(message)
            else:
                logger.info(message)
        except Exception as e:
            print(f"Failed to log event: {e}")
    
    def record_custom_metric(self, metric_name: str, value: float, labels: dict = None):
        """Record custom metric to Cloud Monitoring"""
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/{metric_name}"
            series.resource.type = "cloud_run_revision"
            
            if labels:
                for key, val in labels.items():
                    series.metric.labels[key] = str(val)
            
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": value},
            })
            series.points = [point]
            
            project_name = f"projects/{self.project_id}"
            self.monitoring_client.create_time_series(
                name=project_name, 
                time_series=[series]
            )
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")

# Global instance
telemetry = GCPTelemetry()

def log_event(message: str, severity: str = "INFO"):
    """Convenience function for logging events"""
    telemetry.log_event(message, severity)