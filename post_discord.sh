#!/usr/bin/env bash
# Posts an AI releases briefing to Discord via webhook.
# Reads the briefing from stdin or a file argument.
# Usage:
#   echo "$BRIEFING" | ./post_discord.sh
#   ./post_discord.sh briefing.txt
set -euo pipefail

WEBHOOK="${DISCORD_WEBHOOK_URL:-}"

if [[ -z "$WEBHOOK" ]]; then
  echo "ERROR: DISCORD_WEBHOOK_URL is not set." >&2
  exit 1
fi

# Read from file argument or stdin
if [[ -n "${1:-}" ]]; then
  CONTENT=$(<"$1")
else
  CONTENT=$(cat)
fi

json_encode() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

post_payload() {
  local payload="$1"
  local http_code
  http_code=$(curl -s -o /tmp/discord_response.txt -w "%{http_code}" \
    -X POST "$WEBHOOK" \
    -H "Content-Type: application/json" \
    --data-binary "$payload")
  if [[ "$http_code" != "204" ]]; then
    echo "ERROR: Discord returned HTTP $http_code — $(cat /tmp/discord_response.txt)" >&2
    exit 1
  fi
}

# Extract title from first heading line
TITLE=$(echo "$CONTENT" | grep '^# ' | head -1 | sed 's/^# //')

# Extract bullet-point body
DESCRIPTION=$(echo "$CONTENT" | awk '/^### Top Updates/{found=1; next} /^### Sources/{exit} found && /^- /{print}')

# Extract source URLs
SOURCES=$(echo "$CONTENT" \
  | awk '/^### Sources/,0{print}' \
  | grep -E '^\- \[' \
  | sed 's/^- \[.*\](\(.*\))$/\1/' \
  | sed 's/^/</' | sed 's/$/>/')

# Post main briefing as an embed (supports up to 4096 chars)
TITLE_JSON=$(printf '%s' "$TITLE" | json_encode)
DESC_JSON=$(printf '%s' "$DESCRIPTION" | json_encode)

post_payload "{\"embeds\":[{\"title\":${TITLE_JSON},\"description\":${DESC_JSON},\"color\":5793266}]}"
echo "Posted main briefing."

# Post sources as a follow-up plain message
if [[ -n "$SOURCES" ]]; then
  SOURCES_CONTENT="**Sources**
${SOURCES}"
  SOURCES_JSON=$(printf '%s' "$SOURCES_CONTENT" | json_encode)
  post_payload "{\"content\":${SOURCES_JSON}}"
  echo "Posted sources."
fi

echo "Done — posted to Discord."
