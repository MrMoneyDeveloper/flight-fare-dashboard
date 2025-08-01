#!/usr/bin/env bash
set -euo pipefail

LOGFILE="run_all.log"
: > "$LOGFILE"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

trap 'log "ERROR: script failed at line $LINENO"; exit 1' ERR

log "Installing Python dependencies..."
pip install -r requirements.txt >> "$LOGFILE" 2>&1
log "Python dependencies installed successfully."

log "Extracting and transforming data..."
python etl/extract_excel.py --source data/raw/airlines_flights_data.csv >> "$LOGFILE" 2>&1
python etl/transform.py >> "$LOGFILE" 2>&1
log "Data transformation complete."

log "Building Tailwind CSS..."
pushd ui >> "$LOGFILE"
npm install >> "$LOGFILE" 2>&1
npx tailwindcss -o public/tailwind.css --minify >> "$LOGFILE" 2>&1
popd >> "$LOGFILE"
log "Tailwind build complete."

log "Starting containers with Docker Compose..."
docker compose up --build -d >> "$LOGFILE" 2>&1
log "Docker containers started."

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
