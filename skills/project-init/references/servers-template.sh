#!/bin/bash
# Server management template — adapt to project stack
# Usage: ./scripts/servers.sh [start|stop|restart|status]

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# === CONFIGURE THESE PER PROJECT ===
# Add entries: ("name" "port" "start_command" "pid_file")
declare -a SERVICES=(
  # Example for Node.js:
  # "app:3000:npx next dev --port 3000:.app.pid"
  # Example for Python:
  # "api:8000:python -m uvicorn app.main:app --port 8000 --reload:.api.pid"
  # Example for Go:
  # "server:8080:go run .:.server.pid"
)

# Docker Compose services (set to "yes" if docker-compose.yml exists)
USE_DOCKER="no"
# =================================

is_running() {
  local pid_file="$PROJECT_DIR/$1"
  if [ -f "$pid_file" ]; then
    local pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

kill_port() {
  local port=$1
  local pids=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $5}' | sort -u)
  for p in $pids; do
    [ "$p" != "0" ] && taskkill //F //PID "$p" > /dev/null 2>&1
  done
}

start_services() {
  cd "$PROJECT_DIR"

  # Start Docker if needed
  if [ "$USE_DOCKER" = "yes" ] && [ -f "docker-compose.yml" ]; then
    echo "Starting Docker services..."
    docker compose up -d 2>&1
    sleep 2
  fi

  # Start each service
  for entry in "${SERVICES[@]}"; do
    IFS=':' read -r name port cmd pid_file <<< "$entry"
    if is_running "$pid_file"; then
      echo "$name already running (PID $(cat "$PROJECT_DIR/$pid_file"))"
    else
      echo "Starting $name on :$port..."
      eval "$cmd" > /dev/null 2>&1 &
      echo $! > "$PROJECT_DIR/$pid_file"
      echo "$name started (PID $!)"
    fi
  done
}

stop_services() {
  cd "$PROJECT_DIR"

  for entry in "${SERVICES[@]}"; do
    IFS=':' read -r name port cmd pid_file <<< "$entry"
    if is_running "$pid_file"; then
      local pid=$(cat "$PROJECT_DIR/$pid_file")
      echo "Stopping $name (PID $pid)..."
      kill "$pid" 2>/dev/null
      rm -f "$PROJECT_DIR/$pid_file"
    else
      echo "$name not running"
    fi
    kill_port "$port"
  done

  if [ "$USE_DOCKER" = "yes" ]; then
    echo "Stopping Docker services..."
    docker compose down 2>&1
  fi
}

status_services() {
  echo "=== Project Services ==="
  for entry in "${SERVICES[@]}"; do
    IFS=':' read -r name port cmd pid_file <<< "$entry"
    if is_running "$pid_file"; then
      echo "$name: RUNNING (PID $(cat "$PROJECT_DIR/$pid_file")) on :$port"
      local code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" 2>/dev/null)
      echo "  HTTP $code"
    else
      echo "$name: STOPPED"
    fi
  done

  if [ "$USE_DOCKER" = "yes" ]; then
    echo "--- Docker ---"
    docker compose ps 2>&1
  fi
}

case "${1:-start}" in
  start) start_services ;;
  stop) stop_services ;;
  restart) stop_services; sleep 2; start_services ;;
  status) status_services ;;
  *) echo "Usage: $0 {start|stop|restart|status}" ;;
esac
