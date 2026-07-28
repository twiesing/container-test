#!/bin/bash
# Feinere Messung: kurzer Timeout, damit haengende Requests die Luecke nicht verdecken.
URL="${1:-https://p-d7806b.project.space/commit}"
DUR="${2:-300}"
OUT="${3:-/tmp/pollfast.log}"
end=$(( $(date +%s) + DUR ))
: > "$OUT"
while [ "$(date +%s)" -lt "$end" ]; do
  ts=$(perl -MTime::HiRes=time -e 'printf "%.3f", time')
  resp=$(curl -sS -o /tmp/pf.body -w '%{http_code} %{time_total}' \
         --connect-timeout 1 --max-time 1.5 "$URL" 2>/dev/null)
  code=$(echo "$resp" | awk '{print $1}')
  tt=$(echo "$resp" | awk '{print $2}')
  body=$(head -c 12 /tmp/pf.body 2>/dev/null | tr -d '\n')
  echo "$ts ${code:-000} ${tt:-0} ${body}" >> "$OUT"
  sleep 0.05
done
