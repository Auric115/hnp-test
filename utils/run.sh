#!/bin/bash
echo "[RUN] Starting service..."
docker run -p 8000:8000 --rm hnp-service
