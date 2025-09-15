import os
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
import logging

logger = logging.getLogger(__name__)

def get_credentials():
    """Get GCP credentials from environment or metadata service"""
    try:
        credentials, project_id = default()
        logger.info(f"Authenticated with project: {project_id}")
        return credentials, project_id
    except DefaultCredentialsError as e:
        logger.error(f"Failed to get GCP credentials: {e}")
        raise

def get_project_id():
    """Get GCP project ID from environment or metadata"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        _, project_id = get_credentials()
    return project_id