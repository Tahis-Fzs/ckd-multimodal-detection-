#!/usr/bin/env bash
# Build FYDP code zip (excludes venv, raw data, heavy outputs by default).
# Usage: cd "CKD Dataset" && ./scripts/build_fydp_zip.sh
# Output: ../CKD_FYDP_predefense.zip (parent Title Defence folder)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(dirname "$ROOT")"
ZIP="${ZIP:-$PARENT/CKD_FYDP_predefense.zip}"

cd "$PARENT"
echo "Building $ZIP from CKD Dataset/ ..."

find "CKD Dataset" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

zip -r "$ZIP" "CKD Dataset" \
  -x "CKD Dataset/.venv*" \
  -x "CKD Dataset/**/__pycache__/*" \
  -x "CKD Dataset/.mplconfig/*" \
  -x "CKD Dataset/.jupyter/*" \
  -x "CKD Dataset/outputs/supervisor_runs/*.pkl" \
  -x "CKD Dataset/outputs/supervisor_runs/step2_mimic_checkpoint.pkl"

# Add checkpoint separately (large but needed for demo)
if [[ -f "CKD Dataset/outputs/supervisor_runs/step2_mimic_checkpoint.pkl" ]]; then
  zip -u "$ZIP" "CKD Dataset/outputs/supervisor_runs/step2_mimic_checkpoint.pkl"
fi

echo "Created: $ZIP"
ls -lh "$ZIP"
