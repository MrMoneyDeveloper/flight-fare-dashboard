#!/usr/bin/env bash
set -uo pipefail

LOGFILE="run_all.log"
: > "$LOGFILE"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

trap 'log "ERROR: script failed at line $LINENO"; exit 1' ERR

run_cmd() {
  log "Executing: $*"
  "$@" >> "$LOGFILE" 2>&1
  local status=$?
  if [ $status -ne 0 ]; then
    log "Command failed (exit $status): $*"
    exit $status
  fi
  log "Command succeeded: $*"
}

run_cmd pip install -r requirements.txt

run_cmd python etl/extract_excel.py --source data/raw/airlines_flights_data.csv
run_cmd python etl/transform.py

pushd ui >> "$LOGFILE"
run_cmd npm install
run_cmd npx tailwindcss -o public/tailwind.css --minify
popd >> "$LOGFILE"

run_cmd docker compose up --build -d

log "Checking dashboard availability..."
for i in {1..10}; do
  if curl -sSf http://localhost:8080 > /dev/null; then
    log "Dashboard is available."
    break
  else
    log "Waiting for dashboard..."
    sleep 2
  fi
done

log "Attempting to open dashboard in default browser..."
if command -v xdg-open >/dev/null; then
  xdg-open http://localhost:8080 >> "$LOGFILE" 2>&1 &
elif command -v open >/dev/null; then
  open http://localhost:8080 >> "$LOGFILE" 2>&1 &
else
  log "Could not detect a method to open a browser automatically."
fi

log "All done. Access the dashboard at http://localhost:8080"
