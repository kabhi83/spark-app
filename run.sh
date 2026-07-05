#!/usr/bin/env bash
set -euo pipefail

JOB=${1:-student_processing_job}
ENV=${2:-dev}

uv run python main.py --job "$JOB" --env "$ENV"