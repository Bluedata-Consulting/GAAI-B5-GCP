#!/bin/bash

PROJECT_ID="your-project-id"

echo "Creating secrets in Secret Manager..."

# Create Gemini API key secret
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --project=$PROJECT_ID

# Create MLflow tracking URI secret (if using external MLflow)
echo -n "http://your-mlflow-server:5000" | gcloud secrets create mlflow-tracking-uri \
    --data-file=- \
    --project=$PROJECT_ID

echo "Secrets created successfully!"