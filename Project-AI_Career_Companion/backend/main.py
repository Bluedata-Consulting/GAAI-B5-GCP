from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import mlflow
import traceback
from pathlib import Path
from models.schemas import (
    SkillGapRequest, CareerPlanRequest,
    ReviewRequest, MentorRequest
)
from services import vertex_ai_service, mlflow_service, cloud_monitoring_service
from utils.memory import session_memory
from utils.logger_config import get_logger, RequestLogger

# Initialize logger
logger = get_logger("career_ai_companion")

# Initialize FastAPI app
app = FastAPI(
    title="AI Career Companion (GCP)", 
    version="0.2.0",
    description="AI-powered career guidance and mentorship platform on Google Cloud"
)

# Mount static files for frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend at root
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    static_file = static_dir / "index.html"
    if static_file.exists():
        return FileResponse(static_file)
    return {
        "message": "AI Career Companion API", 
        "docs": "/docs",
        "health": "/health",
        "platform": "Google Cloud Platform"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception in {request.method} {request.url}: {str(exc)}",
        extra={
            'endpoint': str(request.url),
            'method': request.method,
            'exception_type': type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting AI Career Companion Backend (GCP)")
        
        # Initialize MLflow
        logger.info("Initializing MLflow tracking")
        
        # Pre-load commonly used prompts
        prompt_files = {
            "skill_gap_analysis": "prompts/skill_gap_prompt.txt",
            "career_plan_generation": "prompts/career_plan_prompt.txt",
            "performance_review": "prompts/review_prompt.txt",
            "mentor_simulation": "prompts/mentor_prompt.txt"
        }
        
        for prompt_name, file_path in prompt_files.items():
            try:
                mlflow_service.load_prompt_with_fallback(prompt_name, file_path)
                logger.info(f"Successfully loaded/registered prompt: {prompt_name}")
            except Exception as e:
                logger.warning(f"Failed to load prompt {prompt_name}: {e}")
        
        logger.info("AI Career Companion Backend (GCP) started successfully")
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        raise

# Health Check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        with RequestLogger(logger, "/health"):
            cloud_monitoring_service.log_event("health_check")
            logger.info("Health check requested")
            
            frontend_available = (static_dir / "index.html").exists() if static_dir.exists() else False
            
            return {
                "status": "ok", 
                "message": "AI Career Companion (GCP) is running",
                "version": "0.2.0",
                "platform": "Google Cloud Platform",
                "frontend_available": frontend_available,
                "api_docs": "/docs"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")

# Skills Gap Analysis
@app.post("/analyze_skills")
def analyze_skills(req: SkillGapRequest):
    """Analyze skills gap for career development"""
    try:
        with RequestLogger(logger, "/analyze_skills", req.dict()):
            logger.info("Starting skills gap analysis")
            print(req.dict())
            
            # Load prompt with fallback
            prompt_template = mlflow_service.load_prompt_with_fallback(
                "skill_gap_analysis", "prompts/skill_gap_prompt.txt")
            
            # Build prompt
            prompt = prompt_template.format(**req.dict())
            logger.info("Prompt built successfully for skills analysis")
            print(prompt)
            
            # Call Vertex AI
            response = vertex_ai_service.call_vertex_ai(prompt)
            logger.info("Received response from Vertex AI for skills analysis")
            print(response)
            
            # Log to MLflow
            mlflow_service.log_prompt_interaction("analyze_skills", prompt, response)
            
            # Log telemetry
            cloud_monitoring_service.log_event("analyze_skills_completed")
            cloud_monitoring_service.telemetry.record_custom_metric(
                "skills_analysis_requests", 1.0, {"status": "success"}
            )
            
            logger.info("Skills gap analysis completed successfully")
            return {"analysis": response}
            
    except Exception as e:
        logger.error(f"Skills gap analysis failed: {e}", exc_info=True)
        cloud_monitoring_service.log_event("analyze_skills_failed", "ERROR")
        cloud_monitoring_service.telemetry.record_custom_metric(
            "skills_analysis_requests", 1.0, {"status": "error"}
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Skills analysis failed: {str(e)}"
        )

# Career Plan Generator
@app.post("/generate_plan")
def generate_plan(req: CareerPlanRequest):
    """Generate personalized career development plan"""
    try:
        with RequestLogger(logger, "/generate_plan", req.dict()):
            logger.info("Starting career plan generation")
            
            # Load prompt with fallback
            prompt_template = mlflow_service.load_prompt_with_fallback(
                "career_plan_generation", "prompts/career_plan_prompt.txt"
            )
            
            # Build prompt
            prompt = prompt_template.format(**req.dict())
            logger.info("Prompt built successfully for career plan generation")
            
            # Call Vertex AI
            response = vertex_ai_service.call_vertex_ai(prompt)
            logger.info("Received response from Vertex AI for career plan generation")
            
            # Log to MLflow
            mlflow_service.log_prompt_interaction("generate_plan", prompt, response)
            
            # Log telemetry
            cloud_monitoring_service.log_event("generate_plan_completed")
            cloud_monitoring_service.telemetry.record_custom_metric(
                "career_plan_requests", 1.0, {"status": "success"}
            )
            
            logger.info("Career plan generation completed successfully")
            return {"plan": response}
            
    except Exception as e:
        logger.error(f"Career plan generation failed: {e}", exc_info=True)
        cloud_monitoring_service.log_event("generate_plan_failed", "ERROR")
        cloud_monitoring_service.telemetry.record_custom_metric(
            "career_plan_requests", 1.0, {"status": "error"}
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Career plan generation failed: {str(e)}"
        )

# Performance Review Draft
@app.post("/performance_review")
def performance_review(req: ReviewRequest):
    """Generate performance review draft"""
    try:
        with RequestLogger(logger, "/performance_review", req.dict()):
            logger.info("Starting performance review generation")
            
            # Load prompt with fallback
            prompt_template = mlflow_service.load_prompt_with_fallback(
                "performance_review", "prompts/review_prompt.txt"
            )
            
            # Build prompt
            prompt = prompt_template.format(**req.dict())
            logger.info("Prompt built successfully for performance review")
            
            # Call Vertex AI
            response = vertex_ai_service.call_vertex_ai(prompt)
            logger.info("Received response from Vertex AI for performance review")
            
            # Log to MLflow
            mlflow_service.log_prompt_interaction("performance_review", prompt, response)
            
            # Log telemetry
            cloud_monitoring_service.log_event("performance_review_completed")
            cloud_monitoring_service.telemetry.record_custom_metric(
                "performance_review_requests", 1.0, {"status": "success"}
            )
            
            logger.info("Performance review generation completed successfully")
            return {"review": response}
            
    except Exception as e:
        logger.error(f"Performance review generation failed: {e}", exc_info=True)
        cloud_monitoring_service.log_event("performance_review_failed", "ERROR")
        cloud_monitoring_service.telemetry.record_custom_metric(
            "performance_review_requests", 1.0, {"status": "error"}
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Performance review generation failed: {str(e)}"
        )

# Mentorship Simulation
@app.post("/mentor_simulation")
def mentor_simulation(req: MentorRequest):
    """Simulate mentorship conversation"""
    try:
        with RequestLogger(logger, "/mentor_simulation", req.dict()):
            logger.info("Starting mentor simulation")
            
            # Load prompt with fallback
            prompt_template = mlflow_service.load_prompt_with_fallback(
                "mentor_simulation", "prompts/mentor_prompt.txt"
            )
            
            # Build prompt
            prompt = prompt_template.format(**req.dict())
            logger.info("Prompt built successfully for mentor simulation")
            
            # Call Vertex AI
            response = vertex_ai_service.call_vertex_ai(prompt)
            logger.info("Received response from Vertex AI for mentor simulation")
            
            # Log to MLflow
            mlflow_service.log_prompt_interaction("mentor_simulation", prompt, response)
            
            # Log telemetry
            cloud_monitoring_service.log_event("mentor_simulation_completed")
            cloud_monitoring_service.telemetry.record_custom_metric(
                "mentor_simulation_requests", 1.0, {"status": "success"}
            )
            
            logger.info("Mentor simulation completed successfully")
            return {"mentor_response": response}
            
    except Exception as e:
        logger.error(f"Mentor simulation failed: {e}", exc_info=True)
        cloud_monitoring_service.log_event("mentor_simulation_failed", "ERROR")
        cloud_monitoring_service.telemetry.record_custom_metric(
            "mentor_simulation_requests", 1.0, {"status": "error"}
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Mentor simulation failed: {str(e)}"
        )

# Additional utility endpoints
@app.get("/logs/health")
def logs_health():
    """Check logging system health"""
    try:
        logger.info("Logging system health check")
        return {
            "status": "ok",
            "message": "Logging system is operational",
            "logger_name": logger.name,
            "log_level": logger.level,
            "platform": "Google Cloud Platform"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Logging system error: {str(e)}"
        }

# MLflow endpoints for prompt management
@app.get("/prompts/list")
def list_prompts():
    """List available prompts in MLflow"""
    try:
        prompts = mlflow_service.list_available_prompts()
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompts")

@app.post("/prompts/register")
def register_new_prompt(prompt_name: str, prompt_content: str, model: str = 'gemini-1.5-flash'):
    """Register a new prompt in MLflow"""
    try:
        result = mlflow_service.register_prompt(prompt_name, prompt_content, model)
        return {"message": result}
    except Exception as e:
        logger.error(f"Failed to register prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to register prompt")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server with uvicorn (GCP)")
    uvicorn.run(app, host="0.0.0.0", port=8080)