#!/usr/bin/env bash
set -euo pipefail

SPEC="openapi/openapi.yaml"
OUT="src/nli_engine/client/_generated"

# Wipe old generated code
rm -rf "$OUT"
mkdir -p "$OUT"

uv run openapi-generator-cli generate \
	-i "$SPEC" \
	-g python \
	-o "$OUT" \
	--package-name authoring_client \
	--additional-properties=generateSourceCodeOnly=true

# openapi-generator puts code under a package path; flatten or import from it
echo "Client generated at $OUT"
