#!/usr/bin/env bash
set -euo pipefail

# Kill background jobs on exit or Ctrl-C
trap 'kill $(jobs -p) 2>/dev/null' INT TERM EXIT

# Start API, Tailwind watcher and live-server using concurrently
npx concurrently \
  --names "api,css,serve" \
  --prefix "[{name}]" \
  --prefix-colors "cyan.bold,magenta.bold,green.bold" \
  --restart-tries -1 \
  --restart-after 2000 \
  --no-kill-others \
  --no-kill-others-on-fail \
  "cd api && dotnet watch run --urls http://0.0.0.0:8000" \
  "npm run build:css --prefix ui" \
  "npm run serve --prefix ui" &
APP_PID=$!

# Wait for UI to be ready
set +e
npx wait-on http://localhost:8080
set -e

echo "Dashboard available at http://localhost:8080"
if command -v xdg-open >/dev/null; then
  xdg-open http://localhost:8080 >/dev/null 2>&1 &
elif command -v open >/dev/null; then
  open http://localhost:8080 >/dev/null 2>&1 &
fi

# Keep script running until Ctrl-C
wait $APP_PID
