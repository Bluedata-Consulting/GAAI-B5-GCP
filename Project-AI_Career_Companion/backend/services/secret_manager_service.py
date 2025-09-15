from functools import lru_cache
import logging
from google.cloud import secretmanager
from .gcp_auth import get_project_id
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@lru_cache
def _secret_client():
    """Initialize Secret Manager client with caching"""
    return secretmanager.SecretManagerServiceClient()

@lru_cache
def get_secret(secret_name: str) -> str:
    """
    Fetch secret from Google Secret Manager
    
    Args:
        secret_name: Name of the secret in Secret Manager
        
    Returns:
        Secret value as string
    """
    try:
        client = _secret_client()
        project_id = get_project_id()
        
        # Build the resource name
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        logger.debug(f"Fetching secret: {secret_name}")
        response = client.access_secret_version(request={"name": name})
        
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"Successfully retrieved secret: {secret_name}")
        return secret_value
        
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise