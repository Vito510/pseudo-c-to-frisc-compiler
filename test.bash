#!/bin/bash
set -euo pipefail

# Define project paths
ROOT_DIR="$(dirname "$0")"
ANALYZATOR_DIR="$ROOT_DIR/analizator"
TESTS_DIR="$ROOT_DIR/tests"

# Create temporary files for output
GSA_OUT="$(mktemp)"
SA_OUT="$(mktemp)"

# Function to clean up temporary files
cleanup() {
    rm -f "$GSA_OUT" "$SA_OUT"
}
trap cleanup EXIT

# Run all tests
for TEST_DIR in "$TESTS_DIR"/*; do
    if [[ -d "$TEST_DIR" ]]; then
        TEST_NAME=$(basename "$TEST_DIR")
        echo "🔹 Running test: $TEST_NAME"

        SAN_FILE="$(realpath "$TEST_DIR/test.san")"
        IN_FILE="$(realpath "$TEST_DIR/test.in")"
        OUT_FILE="$(realpath "$TEST_DIR/test.out")"

        if [[ ! -f "$SAN_FILE" || ! -f "$IN_FILE" || ! -f "$OUT_FILE" ]]; then
            echo "  ⚠️  Missing test files in $TEST_DIR, skipping..."
            continue
        fi

        # Step 1: Run GSA.py
        python3 "$ROOT_DIR/GSA.py" < "$SAN_FILE" > "$GSA_OUT"

        # Step 2: Run SA.py
        (cd "$ANALYZATOR_DIR" && python3 SA.py < "$IN_FILE" > "$SA_OUT")

        # Step 3: Compare output
        if diff -q "$SA_OUT" "$OUT_FILE" >/dev/null; then
            echo "  ✅ PASSED"
        else
            echo "  ❌ FAILED"
            echo "  --- Diff ---"
            diff --color=always -u "$OUT_FILE" "$SA_OUT" || true
            echo "  ------------"
        fi

        echo
    fi
done


echo "🏁 All tests completed."