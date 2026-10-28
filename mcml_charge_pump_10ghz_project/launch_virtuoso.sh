#!/bin/bash
set -euo pipefail

# Resolve script directory (handles symlinks properly)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
CADENCE_WORK="$SCRIPT_DIR/cadence_work"

if [ ! -d "$CADENCE_WORK" ]; then
    echo "[!] Error: Cadence working directory not found at $CADENCE_WORK" >&2
    exit 1
fi

if ! command -v ngspice >/dev/null 2>&1; then
    echo "[!] ngspice is missing from PATH." >&2
    exit 1
fi
if ! docker image inspect cadence-runner:latest >/dev/null 2>&1; then
    echo "[!] Docker is unavailable or cadence-runner:latest is missing." >&2
    exit 1
fi
if [ ! -f "$CADENCE_WORK/.cdsinit" ] || [ ! -f "$CADENCE_WORK/cds.lib" ]; then
    echo "[!] The Virtuoso project startup files are missing." >&2
    exit 1
fi
if [ ! -x /home/shivam/cadence/IC617/bin/spectre ] || \
   ! /home/shivam/cadence/IC617/bin/spectre -v | grep -q 'ADE ngspice bridge'; then
    echo "[!] The ADE simulator slot is not connected to the local bridge." >&2
    exit 1
fi
if [ ! -f /home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models/models_nom/NMOS_VTG.inc ] || \
   [ ! -f /home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models/models_nom/PMOS_VTG.inc ]; then
    echo "[!] The FreePDK45 transistor model files are missing." >&2
    exit 1
fi

# The user service is enabled for login, and this makes a manual launch recover
# it if the service is inactive after a reboot or desktop-session restart.
systemctl --user start mcml-ade-bridge.service
if ! systemctl --user is-active --quiet mcml-ade-bridge.service; then
    echo "[!] The ADE to ngspice bridge service did not start." >&2
    exit 1
fi

if [ "${1:-}" = "--check" ]; then
    echo "Ready: Docker image, ngspice, Cadence adapter, FreePDK45 models, project files, and ADE bridge service."
    echo "Virtuoso GUI must still be launched after graphical login."
    exit 0
fi

# The bridge selects the one running Cadence container for ADE results.
# Starting another would make that selection ambiguous.
if [ -n "$(docker ps --filter ancestor=cadence-runner:latest --format '{{.ID}}')" ]; then
    echo "[!] A Cadence container is already running. Use its Virtuoso session or close it before launching another." >&2
    exit 1
fi

echo "======================================================="
echo " Starting Cadence Virtuoso IC6.1.7"
echo " Working Directory: $CADENCE_WORK"
echo " Target Library:    shivam (mcml_charge_pump)"
echo "======================================================="

cd "$CADENCE_WORK"
exec /home/shivam/cadence/virtuoso.sh "$@"
