#!/bin/bash

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="ai-career-companion"
REPOSITORY_NAME="career-companion-repo"
SERVICE_ACCOUNT_NAME="career-companion-sa"

echo "Setting up AI Career Companion on Google Cloud..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudbuild.googleapis.com

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="AI Career Companion container repository"

# Create service account
echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="AI Career Companion Service Account" \
    --description="Service account for AI Career Companion application"

# Grant necessary IAM roles
echo "Granting IAM roles..."
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

echo "GCP setup completed!"
echo "Next steps:"
echo "1. Create secrets in Secret Manager"
echo "2. Build and deploy the application"