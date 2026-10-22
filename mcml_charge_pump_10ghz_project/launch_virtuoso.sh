#!/bin/bash
set -e

# Resolve script directory (handles symlinks properly)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
CADENCE_WORK="$SCRIPT_DIR/cadence_work"

if [ ! -d "$CADENCE_WORK" ]; then
    echo "[!] Error: Cadence working directory not found at $CADENCE_WORK" >&2
    exit 1
fi

echo "======================================================="
echo " Starting Cadence Virtuoso IC6.1.7"
echo " Working Directory: $CADENCE_WORK"
echo " Target Library:    shivam (mcml_charge_pump)"
echo "======================================================="

cd "$CADENCE_WORK"
exec /home/shivam/cadence/virtuoso.sh "$@"
