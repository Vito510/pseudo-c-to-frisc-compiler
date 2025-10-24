#!/bin/bash
set -euo pipefail

# Define project paths
ROOT_DIR="$(dirname "$0")"
ANALYZATOR_DIR="$ROOT_DIR/analizator"
TESTS_DIR="$ROOT_DIR/tests"

# Create temporary files for output
GLA_OUT="$(mktemp)"
LA_OUT="$(mktemp)"

# Function to clean up temporary files
cleanup() {
    rm -f "$GLA_OUT" "$LA_OUT"
}
trap cleanup EXIT

# Run all tests
for TEST_DIR in "$TESTS_DIR"/*; do
    if [[ -d "$TEST_DIR" ]]; then
        TEST_NAME=$(basename "$TEST_DIR")
        echo "🔹 Running test: $TEST_NAME"

        LAN_FILE="$(realpath "$TEST_DIR/test.lan")"
        IN_FILE="$(realpath "$TEST_DIR/test.in")"
        OUT_FILE="$(realpath "$TEST_DIR/test.out")"

        if [[ ! -f "$LAN_FILE" || ! -f "$IN_FILE" || ! -f "$OUT_FILE" ]]; then
            echo "  ⚠️  Missing test files in $TEST_DIR, skipping..."
            continue
        fi

        # Step 1: Run GLA.py
        python3 "$ROOT_DIR/GLA.py" < "$LAN_FILE" > "$GLA_OUT"

        # Step 2: Run LA.py
        (cd "$ANALYZATOR_DIR" && python3 LA.py < "$IN_FILE" > "$LA_OUT")

        # Step 3: Compare output
        if diff -q "$LA_OUT" "$OUT_FILE" >/dev/null; then
            echo "  ✅ PASSED"
        else
            echo "  ❌ FAILED"
            echo "  --- Diff ---"
            diff --color=always -u "$OUT_FILE" "$LA_OUT" || true
            echo "  ------------"
        fi

        echo
    fi
done


echo "🏁 All tests completed."
