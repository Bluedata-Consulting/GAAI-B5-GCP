import os
import google.generativeai as genai
from .secret_manager_service import get_secret
from utils.logger_config import get_logger

logger = get_logger(__name__)

# Initialize Vertex AI
try:
    API_KEY = get_secret("gemini-api-key")
    genai.configure(api_key=API_KEY)
    
    # Configure the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    logger.info("Vertex AI Gemini model initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")
    raise

def call_vertex_ai(prompt: str) -> str:
    """
    Call Vertex AI Gemini model with the given prompt
    
    Args:
        prompt: The input prompt for the model
        
    Returns:
        Generated response text
    """
    try:
        logger.info("Calling Vertex AI Gemini model")
        
        # Add system instruction to the prompt
        full_prompt = f"""You are a career planning assistant. {prompt}"""
        
        response = model.generate_content(full_prompt)
        
        if response.candidates and response.candidates[0].content.parts:
            result = response.candidates[0].content.parts[0].text
            logger.info("Successfully received response from Vertex AI")
            return result
        else:
            logger.warning("No valid response from Vertex AI")
            return "I apologize, but I couldn't generate a response. Please try again."
            
    except Exception as e:
        logger.error(f"Error calling Vertex AI: {e}")
        raise Exception(f"AI service error: {str(e)}")