#!/bin/sh
set -e

until mc alias set local "$MINIO_ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
  echo "Waiting for MinIO..."
  sleep 2
done

mc mb "local/${MINIO_BUCKET}" --ignore-existing
mc anonymous set download "local/${MINIO_BUCKET}"
echo "Bucket ${MINIO_BUCKET} ready (public read)"
