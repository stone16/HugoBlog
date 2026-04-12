#!/usr/bin/env bash
# fetch-contributions.sh
# Fetches GitHub contribution data via GraphQL API and writes data/contributions.json
# Used as a build-time step in CI (GitHub Actions).
#
# Requires: GITHUB_TOKEN env var, curl, jq
# On any failure: writes fallback JSON so Hugo build doesn't break.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/data"
OUTPUT_FILE="$OUTPUT_DIR/contributions.json"
GITHUB_USER="stone16"
API_URL="https://api.github.com/graphql"

FALLBACK='{"totalContributions":0,"weeks":[]}'

write_fallback() {
  echo ":: Writing fallback contributions.json"
  mkdir -p "$OUTPUT_DIR"
  echo "$FALLBACK" > "$OUTPUT_FILE"
}

# ── Guard: GITHUB_TOKEN required ──
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo ":: GITHUB_TOKEN not set — skipping contribution fetch"
  write_fallback
  exit 0
fi

# ── Guard: dependencies ──
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo ":: $cmd not found — skipping contribution fetch"
    write_fallback
    exit 0
  fi
done

# ── GraphQL query ──
QUERY='query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            contributionLevel
          }
        }
      }
    }
  }
}'

PAYLOAD=$(jq -n \
  --arg query "$QUERY" \
  --arg login "$GITHUB_USER" \
  '{ query: $query, variables: { login: $login } }')

echo ":: Fetching GitHub contributions for $GITHUB_USER ..."

# ── API call ──
RESPONSE=$(curl -sS --fail-with-body \
  -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$API_URL" 2>&1) || {
  echo ":: API request failed: $RESPONSE"
  write_fallback
  exit 0
}

# ── Validate response has data ──
HAS_ERRORS=$(echo "$RESPONSE" | jq -r 'if .errors then "yes" else "no" end' 2>/dev/null || echo "parse_error")

if [ "$HAS_ERRORS" = "yes" ]; then
  echo ":: GraphQL errors: $(echo "$RESPONSE" | jq -c '.errors')"
  write_fallback
  exit 0
fi

if [ "$HAS_ERRORS" = "parse_error" ]; then
  echo ":: Failed to parse API response"
  write_fallback
  exit 0
fi

# ── Transform response into Hugo data format ──
# Map contributionLevel strings to numeric levels:
#   NONE=0, FIRST_QUARTILE=1, SECOND_QUARTILE=2, THIRD_QUARTILE=3, FOURTH_QUARTILE=4
RESULT=$(echo "$RESPONSE" | jq '{
  totalContributions: .data.user.contributionsCollection.contributionCalendar.totalContributions,
  weeks: [
    .data.user.contributionsCollection.contributionCalendar.weeks[] | {
      contributionDays: [
        .contributionDays[] | {
          count: .contributionCount,
          date: .date,
          level: (
            if .contributionLevel == "NONE" then 0
            elif .contributionLevel == "FIRST_QUARTILE" then 1
            elif .contributionLevel == "SECOND_QUARTILE" then 2
            elif .contributionLevel == "THIRD_QUARTILE" then 3
            elif .contributionLevel == "FOURTH_QUARTILE" then 4
            else 0
            end
          )
        }
      ]
    }
  ]
}' 2>/dev/null) || {
  echo ":: Failed to transform API response"
  write_fallback
  exit 0
}

# ── Validate result has expected shape ──
TOTAL=$(echo "$RESULT" | jq -r '.totalContributions // empty' 2>/dev/null)
if [ -z "$TOTAL" ]; then
  echo ":: Unexpected response shape — missing totalContributions"
  write_fallback
  exit 0
fi

# ── Write output ──
mkdir -p "$OUTPUT_DIR"
echo "$RESULT" > "$OUTPUT_FILE"
echo ":: Wrote contributions.json ($TOTAL total contributions)"
