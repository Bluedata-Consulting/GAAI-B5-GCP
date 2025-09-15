# AI Career Companion - Google Cloud Platform Deployment Guide

## 📌 Problem Statement

The same enterprise career development challenges exist, but now we're leveraging Google Cloud Platform's robust AI and container services for a more scalable, cost-effective solution.

## ✨ GCP Solution Benefits

- **Vertex AI Integration**: Advanced Gemini AI models for natural language processing
- **Cloud Run**: Serverless, auto-scaling container deployment
- **Secret Manager**: Enterprise-grade secrets management
- **Cloud Monitoring**: Comprehensive observability and alerting
- **Artifact Registry**: Secure, private container registry
- **Global Scale**: Multi-region deployment capabilities

## 🏗️ Architecture Overview

```
Internet → Cloud Load Balancer → Cloud Run → Vertex AI (Gemini)
                                      ↓
                               Secret Manager ← Service Account
                                      ↓
                              Cloud Monitoring & Logging
```

## 🔧 Prerequisites

- **Google Cloud CLI** installed and authenticated (`gcloud auth login`)
- **Docker** installed and running
- **Python 3.10+** installed
- **Active GCP Project** with billing enabled
- **Project Owner or Editor** IAM permissions

## 📦 GCP Services Used

| Service | Purpose | Pricing Model |
|---------|---------|---------------|
| **Cloud Run** | Serverless container hosting | Pay-per-request |
| **Artifact Registry** | Private container registry | Storage + bandwidth |
| **Secret Manager** | Secure secrets storage | Per secret version |
| **Vertex AI** | Gemini AI model access | Per token/request |
| **Cloud Monitoring** | Application monitoring | Free tier available |
| **Cloud Logging** | Centralized logging | Free tier available |
| **IAM & Service Accounts** | Authentication | Free |

## 🚀 Quick Start Guide

### 1. Initial Setup

```bash
# Clone and navigate to project
cd ai-career-companion-gcp

# Set your project ID
export PROJECT_ID="your-unique-project-id"
export REGION="us-central1"

# Authenticate with GCP
gcloud auth login
gcloud config set project $PROJECT_ID
```

---

### 2. Enable APIs and Create Resources

```bash
# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudbuild.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="AI Career Companion container repository"

# Create service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="AI Career Companion Service Account" \
    --description="Service account for AI Career Companion application"
```

---

### 3. Grant IAM Permissions

```bash
# Grant necessary IAM roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"
```

---

### 4. Store Secrets in Secret Manager

First, obtain your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

```bash
# Store Gemini API key
echo -n "YOUR_ACTUAL_GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --project=$PROJECT_ID

# Store MLflow URI (if using external MLflow)
MLFLOW_TRACKING_URI="http://20.75.92.162:5000/"
echo -n "$MLFLOW_TRACKING_URI" | gcloud secrets create mlflow-tracking-uri \
    --data-file=- \
    --project=$PROJECT_ID
```

---

### 5. Create Environment Configuration
Make sure the current location on the terminal is Project-AI_Career_Companion folder, so that .env should be created in that folder.

```bash
cat <<EOF > .env.gcp
# GCP Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID

# Application Configuration
APP_ENV=development
API_PORT=8080
SESSION_TIMEOUT_MINUTES=30

# MLflow Configuration
MLFLOW_TRACKING_URI=http://20.75.92.162:5000/

# Region
GCP_REGION=$REGION
EOF
```

---

### 6. Setup Python Virtual Environment
Make sure the environment location is outside the Project-AI_Career_Companion folder.

```bash
cd ..
python3 -m venv gcpenv
source gcpenv/bin/activate
cd Project-AI_Career_Companion/backend
pip install -r requirements.txt
```

---

### 7. Run Backend Locally

```bash
# Copy GCP environment file
cp .env.gcp .env

# Run locally
uvicorn main:app --reload --port 8080
```

* Test health: [http://127.0.0.1:8080/health](http://127.0.0.1:8080/health)
* Open API docs: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

---

### 8. Run Frontend Locally

Start a New Terminal, navigate to `frontend` folder, and run:
```bash
python -m http.server 8081
```

Open browser: [http://127.0.0.1:8081](http://127.0.0.1:8081)

---

### 9. Build & Test Docker Image
Make sure the current location is Project-AI_Career_Companion

```bash
DOCKER_IMAGE=career-backend-gcp

# Build using GCP Dockerfile
cd ..
docker build -f Dockerfile.gcp -t $DOCKER_IMAGE .

# Run locally
docker run -p 8080:8080 --name $DOCKER_IMAGE-container \
  -e GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  -e APP_ENV=development \
  $DOCKER_IMAGE

# Test
curl http://127.0.0.1:8080/health
```

---

### 10. Push Image to Artifact Registry

```bash
# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Tag and push image
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest"
docker tag $DOCKER_IMAGE $IMAGE_URL
docker push $IMAGE_URL
```

---

### 11. Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URL \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},APP_ENV=production" \
    --memory=4Gi \
    --cpu=2 \
    --timeout=300 \
    --concurrency=100 \
    --max-instances=10 \
    --port=8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "Deployment completed!"
echo "Service URL: $SERVICE_URL"
echo "Health check: $SERVICE_URL/health"
echo "API documentation: $SERVICE_URL/docs"
```

---

### 12. Test Deployment

```bash
# Test health endpoint
curl $SERVICE_URL/health

# Test skills analysis endpoint
curl -X POST $SERVICE_URL/analyze_skills \
  -H "Content-Type: application/json" \
  -d '{
    "current_role": "Junior Developer",
    "target_role": "Senior Developer",
    "skills": ["Python", "Git"],
    "desired_skills": ["Docker", "Kubernetes", "System Design"]
  }'
```

---

### 13. Monitoring and Observability

#### View Cloud Run Logs
```bash
# Stream live logs
gcloud run services logs tail $SERVICE_NAME --region=$REGION

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=50
```

#### View Metrics in Cloud Monitoring
```bash
# Open Cloud Monitoring dashboard
echo "View metrics at: https://console.cloud.google.com/monitoring/dashboards"

# Create custom metric filters
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.message:\"Skills gap analysis\"" --limit=10
```

---

### 14. Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region=$REGION --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete $REPOSITORY_NAME --location=$REGION --quiet

# Delete secrets
gcloud secrets delete gemini-api-key --quiet
gcloud secrets delete mlflow-tracking-uri --quiet

# Delete service account
gcloud iam service-accounts delete ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --quiet

echo "Cleanup completed!"
```

---

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Issues**
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Check current project
gcloud config get-value project
```

2. **Service Account Permissions**
```bash
# Check current IAM bindings
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:${SERVICE_ACCOUNT_NAME}@*"
```

3. **Secret Manager Access**
```bash
# Test secret access
gcloud secrets versions access latest --secret="gemini-api-key"
```

4. **Container Registry Authentication**
```bash
# Re-authenticate Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
```

### Debug Mode

Enable debug logging:
```bash
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="LOG_LEVEL=DEBUG"
```

---

## 🚀 Advanced Features

### 1. Multi-Region Deployment

```bash
# Deploy to additional regions
SECONDARY_REGION="us-west1"

gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URL \
    --region=$SECONDARY_REGION \
    --allow-unauthenticated \
    --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

### 2. Load Balancing with Cloud Load Balancer

```bash
# Create global load balancer for multi-region setup
gcloud compute backend-services create career-companion-backend \
    --global \
    --protocol=HTTP \
    --health-checks=career-companion-health-check
```

### 3. Custom Domain Setup

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service=$SERVICE_NAME \
    --domain=career-companion.yourdomain.com \
    --region=$REGION
```

---

## 💰 Cost Optimization

### Resource Limits
```bash
# Deploy with cost-optimized settings
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URL \
    --region=$REGION \
    --cpu=1 \
    --memory=2Gi \
    --concurrency=80 \
    --max-instances=5 \
    --min-instances=0 \
    --cpu-throttling
```

### Budget Alerts
```bash
# Set up budget alerts (requires billing account ID)
gcloud billing budgets create \
    --billing-account=YOUR_BILLING_ACCOUNT_ID \
    --display-name="Career Companion Budget" \
    --budget-amount=50USD \
    --threshold-rule=percent=90,spend-basis=CURRENT_SPEND
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
- [Cloud Monitoring Guides](https://cloud.google.com/monitoring/docs)
- [GCP Cost Optimization](https://cloud.google.com/cost-optimization)

---

## 🎯 Next Steps

1. **Enhanced Features**
   - Add user authentication with Firebase Auth
   - Implement caching with Memorystore (Redis)
   - Add database persistence with Cloud SQL
   - Integrate with Workspace APIs

2. **Production Readiness**
   - Set up proper CI/CD pipelines with Cloud Build
   - Implement comprehensive monitoring dashboards
   - Add performance testing with Cloud Load Testing
   - Configure backup and disaster recovery strategies

3. **Scaling Considerations**
   - Multi-region deployment strategy
   - CDN integration with Cloud CDN
   - Auto-scaling policies and resource optimization
   - Advanced security with Cloud Armor

---
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
- [Cloud Monitoring Guides](https://cloud.google.com/monitoring/docs)
- [GCP Cost Optimization](https://cloud.google.com/cost-optimization)

## 🎯 Next Steps

1. **Enhanced Features**
   - Add user authentication with Firebase Auth
   - Implement caching with Memorystore (Redis)
   - Add database persistence with Cloud SQL
   - Integrate with Workspace APIs

2. **Production Readiness**
   - Set up proper CI/CD pipelines
   - Implement comprehensive monitoring
   - Add performance testing
   - Configure backup strategies

3. **Scaling Considerations**
   - Multi-region deployment
   - CDN integration with Cloud CDN
   - Load balancing with Cloud Load Balancer
   - Auto-scaling policies