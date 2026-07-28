# Downtime-Messung bei Container-Redeployment

Misst aus Endnutzersicht (öffentliche URL), wie lange eine Container-Anwendung
während eines Redeployments mit 502/503 antwortet.

## Aufbau

Der Container ist ein `nginx:alpine`, der unter `/commit` den Git-Commit
ausliefert, aus dem sein Image gebaut wurde (siehe [`Dockerfile`](../Dockerfile)).
Dadurch ist am Response erkennbar, ob schon die neue Instanz antwortet.

Deployment läuft über den mStudio Pull-Image-Webhook, siehe
[`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).

## Ablauf

```bash
./poll.sh https://p-d7806b.project.space/commit 1800 messung.log &
./driver.sh 10 driver.log
./auswertung.py messung.log
```

- `poll.sh` fragt die URL ca. 4x/s ab und protokolliert Zeitstempel, HTTP-Code
  und ausgelieferten Commit. Timeout 1,5 s, damit hängende Requests das
  Ausfallfenster nicht verdecken.
- `driver.sh` stößt N Deployments nacheinander an und wartet jeweils auf den
  Abschluss des GitHub-Actions-Runs.
- `auswertung.py` bestimmt je Deployment das Ausfallfenster: von der letzten
  guten Antwort mit altem Commit bis zur ersten guten Antwort mit neuem Commit.

## Rohdaten

[`messung-2026-07-28.log`](messung-2026-07-28.log) — 10 Deployments,
28.07.2026, 13:36–13:49 Uhr.
