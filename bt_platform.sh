#!/bin/bash
# Launcher script for BT Platform tools

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

case "$1" in
  demo)
    echo "Running BT Platform demo..."
    python3 "$SCRIPT_DIR/bt_platform/demo.py"
    ;;
  server)
    echo "Starting BT Platform API server on port 8081..."
    python3 "$SCRIPT_DIR/bt_platform/endpoints/predictions_v2.py"
    ;;
  test)
    echo "Testing API endpoints..."
    if ! curl -s http://localhost:8081/v2/alpha/top?limit=1 >/dev/null 2>&1; then
      echo "❌ Server not running. Start with: $0 server"
      exit 1
    fi
    echo "✓ Server is running"
    echo ""
    echo "Testing /v2/predict/timing/TEST-001:"
    curl -s http://localhost:8081/v2/predict/timing/TEST-001 | python3 -m json.tool
    echo ""
    echo "Testing /v2/alpha/top?limit=3:"
    curl -s "http://localhost:8081/v2/alpha/top?limit=3" | python3 -m json.tool
    ;;
  *)
    echo "BT Platform - Biotech Catalyst Prediction API v2"
    echo ""
    echo "Usage: $0 {demo|server|test}"
    echo ""
    echo "Commands:"
    echo "  demo    - Run interactive demonstration"
    echo "  server  - Start API server on port 8081"
    echo "  test    - Test API endpoints (requires running server)"
    echo ""
    echo "Examples:"
    echo "  $0 demo"
    echo "  $0 server &"
    echo "  $0 test"
    exit 1
    ;;
esac
