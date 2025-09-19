#!/bin/bash
echo "Starting FastAPI application..."

# Ensure Python can import the top-level `app` package when WORKDIR is `/app`.
# Adding `/` to PYTHONPATH makes `/app` importable as the `app` package (PEP 420 implicit namespace).
export PYTHONPATH="/:${PYTHONPATH}"

uvicorn main:app --host ${HOST:-0.0.0.0} --port ${APP_PORT:-8000} --reload