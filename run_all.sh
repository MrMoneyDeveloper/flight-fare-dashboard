#!/usr/bin/env bash
set -uo pipefail

LOGFILE="$(pwd)/run_all.log"
: > "$LOGFILE"

# Colour helpers ------------------------------------------------------------
COL_RESET="\033[0m"
COL_INFO="\033[36m"   # cyan
COL_ERR="\033[31m"    # red

log() {
  printf "%b[%s]%b %s\n" "$COL_INFO" "$(date +'%Y-%m-%d %H:%M:%S')" \
    "$COL_RESET" "$*" | tee -a "$LOGFILE"
}

trap 'log "${COL_ERR}ERROR: script failed at line $LINENO${COL_RESET}"; exit 1' ERR

run_cmd() {
  log "Executing: $*"
  "$@" 2>&1 | tee -a "$LOGFILE"
  local status=${PIPESTATUS[0]}
  if [ "$status" -ne 0 ]; then
    log "${COL_ERR}Command failed (exit $status): $*${COL_RESET}"
    exit "$status"
  fi
  log "Command succeeded: $*"
}

# Like run_cmd but continue on failure (log error and proceed)
run_cmd_allow_fail() {
  log "Executing (non-fatal): $*"
  "$@" 2>&1 | tee -a "$LOGFILE"
  local status=${PIPESTATUS[0]}
  if [ "$status" -ne 0 ]; then
    log "${COL_ERR}Command failed (exit $status) but continuing: $*${COL_RESET}"
  else
    log "Command succeeded: $*"
  fi
}

run_cmd pip install -r requirements.txt

run_cmd_allow_fail python etl/extract_excel.py --source data/raw/airlines_flights_data.csv
run_cmd_allow_fail python etl/transform.py

# Warn if no data was produced
if ! ls data/gold/*.parquet >/dev/null 2>&1; then
  log "${COL_ERR}No data available; dashboard will load without data${COL_RESET}"
fi

log "Building UI assets..."
pushd ui > /dev/null || exit
run_cmd npm install
run_cmd npx tailwindcss -o public/tailwind.css --minify
popd > /dev/null || exit

log "Starting API..."
pushd api > /dev/null || exit
dotnet run --urls http://localhost:8000 >> ../run_all.log 2>&1 &
API_PID=$!
popd > /dev/null || exit

log "Starting local web server..."
pushd ui > /dev/null || exit

# Use python3 if available, otherwise fall back to python
if command -v python3 >/dev/null; then
  PYTHON_CMD=python3
else
  PYTHON_CMD=python
fi

$PYTHON_CMD -m http.server 8080 >> ../run_all.log 2>&1 &
UI_PID=$!
popd > /dev/null || exit

cleanup() {
  log "Stopping..."
  kill "$API_PID" "$UI_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT
log "Processes started. API on http://localhost:8000, dashboard on http://localhost:8080"

log "Checking dashboard availability..."
for _ in {1..10}; do
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
elif command -v cmd.exe >/dev/null; then
  cmd.exe /c start "" http://localhost:8080 >> "$LOGFILE" 2>&1 &
elif command -v powershell.exe >/dev/null; then
  powershell.exe -NoProfile Start-Process http://localhost:8080 >> "$LOGFILE" 2>&1 &
elif command -v python3 >/dev/null; then
  python3 -m webbrowser http://localhost:8080 >> "$LOGFILE" 2>&1 &
elif command -v python >/dev/null; then
  python -m webbrowser http://localhost:8080 >> "$LOGFILE" 2>&1 &
else
  log "Could not detect a method to open a browser automatically."
fi

log "All done. Access the dashboard at http://localhost:8080"
wait $API_PID $UI_PID || true
