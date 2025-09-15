import mlflow
import os
from typing import Optional, List, Dict
from .secret_manager_service import get_secret
from utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize MLflow
try:
    # Try to get MLflow tracking URI from Secret Manager
    try:
        MLFLOW_TRACKING_URI = get_secret("mlflow-tracking-uri")
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        logger.info(f"MLflow tracking URI set from Secret Manager: {MLFLOW_TRACKING_URI}")
    except Exception as secret_error:
        # Fallback to environment variable or default
        MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        logger.warning(f"Using fallback MLflow URI: {MLFLOW_TRACKING_URI}")
        
except Exception as e:
    logger.error(f"Failed to initialize MLflow tracking URI: {e}", exc_info=True)
    raise

def register_prompt(prompt_name: str, prompt: str, model: str = 'gemini-1.5-flash') -> str:
    """
    Register a new prompt in MLflow
    
    Args:
        prompt_name: Name of the prompt to register
        prompt: The actual prompt template
        model: Model name for tagging (default: gemini-1.5-flash)
    
    Returns:
        Success message
    """
    try:
        logger.info(f"Starting prompt registration for: {prompt_name}")
        
        prompt_obj = mlflow.genai.register_prompt(
            name=prompt_name, 
            template=prompt,
            commit_message="Prompt Registration - GCP Deployment",
            tags={
                "author": "AI Career Companion",
                "task": "Content Generation",
                "language": "en",
                "llm": model,
                "platform": "gcp",
                "vertex_ai_model": model
            }
        )
        
        logger.info(f"Prompt registered successfully: '{prompt_obj.name}' (version {prompt_obj.version})")
        
        # Deploy prompt to production
        mlflow.set_prompt_alias(prompt_name, alias="production", version=1)
        logger.info(f"Prompt deployed to production: {prompt_name}")
        
        return f"Prompt '{prompt_name}' successfully registered and deployed (version {prompt_obj.version})"
        
    except Exception as e:
        logger.error(f"Failed to register prompt '{prompt_name}': {e}", exc_info=True)
        raise

def load_prompt(prompt_name: str, alias: str = 'production'):
    """
    Load a prompt from MLflow registry
    
    Args:
        prompt_name: Name of the prompt to load
        alias: Alias to load (default: production)
    
    Returns:
        Loaded prompt object
    """
    try:
        path = f"prompts:/{prompt_name}@{alias}"
        logger.info(f"Attempting to load prompt from path: {path}")
        
        prompt = mlflow.genai.load_prompt(name_or_uri=path)
        logger.info(f"Prompt loaded successfully: {prompt_name}")
        
        return prompt
        
    except Exception as e:
        logger.error(f"Failed to load prompt '{prompt_name}' with alias '{alias}': {e}", exc_info=True)
        raise

def load_prompt_with_fallback(prompt_name: str, prompt_file_path: str, alias: str = 'production'):
    """
    Load prompt from MLflow, with fallback to register and retry if not found
    
    Args:
        prompt_name: Name of the prompt to load
        prompt_file_path: Path to the prompt file for registration fallback
        alias: Alias to load (default: production)
    
    Returns:
        Loaded prompt object or prompt content as string
    """
    try:
        logger.info(f"Attempting to load prompt: {prompt_name}")
        return load_prompt(prompt_name, alias)
        
    except Exception as load_error:
        logger.warning(f"Failed to load prompt '{prompt_name}': {load_error}")
        logger.info(f"Attempting to register prompt from file: {prompt_file_path}")
        
        try:
            # Read prompt from file
            if not os.path.exists(prompt_file_path):
                error_msg = f"Prompt file not found: {prompt_file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            logger.info(f"Read prompt content from file: {prompt_file_path}")
            
            # Register the prompt
            register_result = register_prompt(prompt_name, prompt_content)
            logger.info(f"Registration result: {register_result}")
            
            # Retry loading after registration
            logger.info(f"Retrying prompt load after registration: {prompt_name}")
            return load_prompt(prompt_name, alias)
            
        except Exception as register_error:
            logger.error(f"Failed to register and load prompt '{prompt_name}': {register_error}", exc_info=True)
            
            # Final fallback: return the file content directly
            try:
                with open(prompt_file_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                logger.warning(f"Using direct file content for prompt: {prompt_name}")
                
                # Create a simple template-like object
                class SimplePromptTemplate:
                    def __init__(self, template):
                        self.template = template
                    
                    def format(self, **kwargs):
                        return self.template.format(**kwargs)
                
                return SimplePromptTemplate(prompt_content)
                
            except Exception as file_error:
                logger.error(f"Final fallback failed for prompt '{prompt_name}': {file_error}")
                raise

def log_prompt_interaction(endpoint: str, prompt: str, response: str, model: str = 'gemini-1.5-flash'):
    """
    Log prompt interaction to MLflow
    
    Args:
        endpoint: API endpoint name
        prompt: The prompt used
        response: The response received
        model: Model used for generation
    """
    try:
        logger.info(f"Logging prompt interaction for endpoint: {endpoint}")
        
        with mlflow.start_run(run_name=f"{endpoint}_run_gcp"):
            # Log parameters
            mlflow.log_param("endpoint", endpoint)
            mlflow.log_param("model", model)
            mlflow.log_param("platform", "gcp")
            mlflow.log_param("vertex_ai_model", model)
            mlflow.log_param("prompt_length", len(prompt))
            mlflow.log_param("response_length", len(response))
            
            # Log metrics
            mlflow.log_metric("prompt_tokens", len(prompt.split()))
            mlflow.log_metric("response_tokens", len(response.split()))
            
            # Log as artifacts for better organization
            mlflow.log_text(prompt, f"prompt_{endpoint}.txt")
            mlflow.log_text(response, f"response_{endpoint}.txt")
            
            # Log additional metadata
            mlflow.set_tag("environment", os.getenv("APP_ENV", "development"))
            mlflow.set_tag("cloud_provider", "gcp")
            mlflow.set_tag("service", "ai_career_companion")
            
        logger.info(f"Prompt interaction logged successfully for: {endpoint}")
        
    except Exception as e:
        logger.error(f"Failed to log prompt interaction for '{endpoint}': {e}", exc_info=True)
        # Don't raise here as logging failure shouldn't break the main flow

def list_available_prompts() -> List[Dict]:
    """
    List all available prompts in MLflow registry
    
    Returns:
        List of prompt information dictionaries
    """
    try:
        logger.info("Retrieving list of available prompts from MLflow")
        
        # Get MLflow client
        client = mlflow.MlflowClient()
        
        # Search for registered prompts
        prompts = []
        try:
            # This is a simplified approach - MLflow's prompt registry API may vary
            # You might need to adapt this based on your MLflow version
            experiments = client.search_experiments()
            
            for exp in experiments:
                if "prompt" in exp.name.lower():
                    runs = client.search_runs(
                        experiment_ids=[exp.experiment_id],
                        max_results=10
                    )
                    
                    for run in runs:
                        prompt_info = {
                            "name": run.data.tags.get("mlflow.runName", "unknown"),
                            "experiment_id": exp.experiment_id,
                            "run_id": run.info.run_id,
                            "status": run.info.status,
                            "created_at": run.info.start_time,
                            "tags": run.data.tags
                        }
                        prompts.append(prompt_info)
            
        except Exception as search_error:
            logger.warning(f"Advanced prompt search failed: {search_error}")
            # Return basic prompt list
            prompts = [
                {"name": "skill_gap_analysis", "status": "available"},
                {"name": "career_plan_generation", "status": "available"},
                {"name": "performance_review", "status": "available"},
                {"name": "mentor_simulation", "status": "available"}
            ]
        
        logger.info(f"Found {len(prompts)} prompts in registry")
        return prompts
        
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}", exc_info=True)
        return []

def get_prompt_metrics(prompt_name: str, days: int = 7) -> Dict:
    """
    Get usage metrics for a specific prompt
    
    Args:
        prompt_name: Name of the prompt
        days: Number of days to look back (default: 7)
    
    Returns:
        Dictionary with prompt usage metrics
    """
    try:
        logger.info(f"Retrieving metrics for prompt: {prompt_name}")
        
        client = mlflow.MlflowClient()
        
        # Search for runs related to this prompt
        runs = client.search_runs(
            experiment_ids=[],
            filter_string=f"tags.prompt_name = '{prompt_name}'",
            max_results=100
        )
        
        # Calculate metrics
        total_runs = len(runs)
        avg_prompt_length = 0
        avg_response_length = 0
        success_rate = 0
        
        if runs:
            prompt_lengths = [run.data.metrics.get("prompt_tokens", 0) for run in runs]
            response_lengths = [run.data.metrics.get("response_tokens", 0) for run in runs]
            
            avg_prompt_length = sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0
            avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
            
            successful_runs = [run for run in runs if run.info.status == "FINISHED"]
            success_rate = len(successful_runs) / total_runs if total_runs > 0 else 0
        
        metrics = {
            "prompt_name": prompt_name,
            "total_runs": total_runs,
            "avg_prompt_tokens": round(avg_prompt_length, 2),
            "avg_response_tokens": round(avg_response_length, 2),
            "success_rate": round(success_rate * 100, 2),
            "period_days": days
        }
        
        logger.info(f"Retrieved metrics for {prompt_name}: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics for prompt '{prompt_name}': {e}", exc_info=True)
        return {
            "prompt_name": prompt_name,
            "error": str(e),
            "total_runs": 0
        }

def update_prompt_alias(prompt_name: str, version: int, alias: str = "production"):
    """
    Update the alias for a prompt version
    
    Args:
        prompt_name: Name of the prompt
        version: Version number to promote
        alias: Alias to set (default: production)
    """
    try:
        logger.info(f"Updating alias '{alias}' for prompt '{prompt_name}' to version {version}")
        
        mlflow.set_prompt_alias(prompt_name, alias=alias, version=version)
        
        logger.info(f"Successfully updated alias '{alias}' for '{prompt_name}' to version {version}")
        
    except Exception as e:
        logger.error(f"Failed to update alias for prompt '{prompt_name}': {e}", exc_info=True)
        raise

def cleanup_old_runs(days_to_keep: int = 30):
    """
    Clean up old MLflow runs to manage storage
    
    Args:
        days_to_keep: Number of days of runs to keep (default: 30)
    """
    try:
        logger.info(f"Starting cleanup of MLflow runs older than {days_to_keep} days")
        
        client = mlflow.MlflowClient()
        
        # This is a placeholder - implement based on your cleanup policy
        # Be careful with this in production!
        
        logger.warning("Cleanup functionality not fully implemented - manual review required")
        
    except Exception as e:
        logger.error(f"Failed to cleanup old runs: {e}", exc_info=True)