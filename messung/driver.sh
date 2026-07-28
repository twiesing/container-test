#!/bin/bash
# Stoesst N Deployments nacheinander an und wartet jeweils auf den Abschluss des Runs.
set -u
cd /private/tmp/container/container-test || exit 1
N="${1:-10}"
LOG="${2:-/tmp/driver.log}"
: > "$LOG"
for i in $(seq 1 "$N"); do
  printf 'build %s\n' "$(date +%s)" > trigger.txt
  git add trigger.txt
  git -c user.name="Tobias Wiesing" -c user.email="t.wiesing@mittwald.de" \
      commit -q -m "chore: Trigger aktualisieren ($i/$N)"
  git push -q origin main
  sha="$(git rev-parse HEAD)"
  echo "$i push $(date +%s) $sha" >> "$LOG"

  # auf Abschluss des zugehoerigen Runs warten
  for _ in $(seq 1 120); do
    sleep 10
    st="$(gh run list -L 1 --json status,headSha -q '.[0]|"\(.status) \(.headSha)"' 2>/dev/null)"
    case "$st" in
      "completed $sha") break ;;
    esac
  done
  echo "$i done $(date +%s) $(gh run list -L 1 --json conclusion -q '.[0].conclusion')" >> "$LOG"
  sleep 15
done
echo "ALLE FERTIG" >> "$LOG"
