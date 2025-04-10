#!/bin/bash
set -e

PROJECT_ID="yogonet-456319"
REGION="us-west4"
REPO="docker-repo"
IMAGE_NAME="yogonet-scraper"
JOB_NAME="scraper-job"

# Construir imagen con contexto explícito
docker build --no-cache -t $IMAGE_NAME .

# Autenticación y push
gcloud auth configure-docker ${REGION}-docker.pkg.dev
docker tag $IMAGE_NAME ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest

# Desplegar como Cloud Run Job
gcloud run jobs create ${JOB_NAME} \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest \
  --region ${REGION} \
  --memory 4Gi \
  --cpu=2 \
  --service-account=scraper-sa@yogonet-456319.iam.gserviceaccount.com \
  --set-env-vars "BQ_TABLE_ID=yogonet-456319.yogonet_data.articles" \
  --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=scraper-creds:latest \
  --max-retries=3 \
  --task-timeout=3600s

echo "Job creado: ${JOB_NAME}"
echo "Para ejecutar el job manualmente:"
echo "gcloud run jobs execute ${JOB_NAME} --region ${REGION}"
