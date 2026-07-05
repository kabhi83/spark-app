@echo off
:: Capture positional arguments or use fallbacks
SET JOB=%1
IF "%JOB%"=="" SET JOB=student_processing_job

SET ENV=%2
IF "%ENV%"=="" SET ENV=dev

:: Execute via uv
uv run python main.py --job %JOB% --env %ENV%