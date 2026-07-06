#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

LIMIT="${LIMIT:-10}"
URL_FILE="${URL_FILE:-$SCRIPT_DIR/urls.txt}"

if [[ ! -f "$URL_FILE" ]]; then
  echo "URL file not found: $URL_FILE" >&2
  exit 1
fi

URLS=()

while IFS= read -r line || [[ -n "$line" ]]; do
  url="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  [[ -z "$url" ]] && continue
  [[ "$url" =~ ^# ]] && continue

  URLS+=("$url")
done < "$URL_FILE"

if [[ ${#URLS[@]} -eq 0 ]]; then
  echo "No URLs found in: $URL_FILE" >&2
  exit 1
fi

cd "$ROOT_DIR"

TOTAL=${#URLS[@]}

for i in "${!URLS[@]}"; do
  url="${URLS[$i]}"
  current=$((i + 1))

  echo "========================================"
  echo "Collecting [$current/$TOTAL]: $url"
  echo "========================================"

  python3 src/main.py --collect-jobs --url "$url" --limit "$LIMIT"
done

echo "========================================"
echo "All collections completed."
echo "========================================"
