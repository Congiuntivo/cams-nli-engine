#!/usr/bin/env bash
set -euo pipefail

SPEC="openapi/openapi.yaml"
PACKAGE="nli_engine.client._generated.authoring_client"
OUT="src/nli_engine/client/_generated"

# Generate into a temp dir because openapi-generator creates a directory
# tree matching the fully-qualified package name (e.g. nli_engine/client/_generated/authoring_client/).
# We then lift the innermost package into place.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

uv run openapi-generator-cli generate \
	-i "$SPEC" \
	-g python \
	-o "$TMP" \
	--package-name "$PACKAGE" \
	--additional-properties=generateSourceCodeOnly=true

# Wipe old generated code and move the new package into place
rm -rf "$OUT"
mkdir -p "$OUT"
mv "$TMP/nli_engine/client/_generated/authoring_client" "$OUT/"

# Supporting files (README, requirements.txt, etc.) land at $TMP root
# Copy anything else you care about, e.g.:
[ -f "$TMP/README.md" ] && cp "$TMP/README.md" "$OUT/authoring_client_README.md"

echo "Client generated at $OUT/authoring_client"
