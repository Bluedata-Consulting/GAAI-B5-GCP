#!/bin/bash

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="ai-career-companion"
REPOSITORY_NAME="career-companion-repo"
SERVICE_ACCOUNT_NAME="career-companion-sa"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest"

echo "Building and deploying AI Career Companion..."

# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.gcp -t $IMAGE_URL .

# Push to Artifact Registry
echo "Pushing image to Artifact Registry..."
docker push $IMAGE_URL

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URL \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --memory=4Gi \
    --cpu=2 \
    --timeout=300 \
    --concurrency=100 \
    --max-instances=10

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "Deployment completed!"
echo "Service URL: $SERVICE_URL"
echo "Health check: $SERVICE_URL/health"
echo "API documentation: $SERVICE_URL/docs"