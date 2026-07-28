#!/usr/bin/env python3
"""Wertet ein Poll-Log aus und gibt die Ausfallfenster je Deployment aus.

Ein Deployment wird daran erkannt, dass sich der ausgelieferte Commit
ueber ein Fehlerfenster hinweg aendert. Fehlerfenster ohne Commit-Wechsel
sind Stoerungen ohne Deployment und werden getrennt ausgewiesen.

Je Deployment werden zwei Werte ausgewiesen:

  harte Phase  laengste ununterbrochene Fehlerkette
  bis stabil   letzte gute Antwort mit altem Commit bis zur ersten guten
               Antwort, nach der keine Fehler mehr folgen

Beide unterscheiden sich, wenn die Umschaltung flappt, also 200er und 503er
sich eine Zeit lang abwechseln.

    ./auswertung.py messung-2026-07-28.log
"""
import statistics
import sys

GAP = 15.0  # Sekunden ohne Fehler, die zwei Fenster voneinander trennen


def lade(pfad):
    rows = []
    for line in open(pfad):
        p = line.split()
        if len(p) >= 4:
            rows.append((float(p[0]), p[1], p[3][:12]))
    return rows


def fenster(rows):
    bursts, cur = [], []
    for i, (ts, code, _) in enumerate(rows):
        if code != "200":
            if cur and ts - cur[-1][0] > GAP:
                bursts.append(cur)
                cur = []
            cur.append((ts, code, i))
    if cur:
        bursts.append(cur)
    return bursts


def harte_phase(rows, burst):
    """Laengste ununterbrochene Fehlerkette, gemessen von der guten Antwort
    davor bis zur guten Antwort danach."""
    laengste = 0.0
    kette = []
    for _, _, idx in burst + [(None, None, None)]:
        if kette and idx == kette[-1] + 1:
            kette.append(idx)
            continue
        if kette:
            davor = rows[kette[0] - 1][0]
            danach = rows[kette[-1] + 1][0]
            laengste = max(laengste, danach - davor)
        kette = [idx] if idx is not None else []
    return laengste


def main():
    rows = lade(sys.argv[1] if len(sys.argv) > 1 else "messung-2026-07-28.log")
    deployments, stoerungen = [], []
    for b in fenster(rows):
        vorher = [r for r in rows[:b[0][2]] if r[1] == "200"][-1]
        nachher = rows[b[-1][2] + 1]
        fehler = sum(1 for r in rows[b[0][2]:b[-1][2] + 1] if r[1] != "200")
        gesamt = b[-1][2] - b[0][2] + 1
        eintrag = (vorher[2], nachher[2], fehler, gesamt,
                   harte_phase(rows, b), nachher[0] - vorher[0])
        (deployments if vorher[2] != nachher[2] else stoerungen).append(eintrag)

    print(f"{'#':>2} {'alt':>12} -> {'neu':<12} {'Fehler':>10} "
          f"{'harte Phase':>12} {'bis stabil':>11}")
    for n, (alt, neu, fehler, gesamt, hart, stabil) in enumerate(deployments, 1):
        print(f"{n:>2} {alt:>12} -> {neu:<12} {fehler:>4}/{gesamt:<5} "
              f"{hart:11.2f}s {stabil:10.2f}s")

    for name, spalte in (("harte Phase", 4), ("bis stabil", 5)):
        v = [d[spalte] for d in deployments]
        print(f"\n{name}: n={len(v)}  min={min(v):.2f}s  "
              f"median={statistics.median(v):.2f}s  mean={statistics.mean(v):.2f}s  "
              f"max={max(v):.2f}s  <= 5s: {sum(1 for t in v if t <= 5)}/{len(v)}")

    print(f"\nStoerungen ohne Deployment: {len(stoerungen)} "
          f"({[round(s[5], 2) for s in stoerungen]}s)")


if __name__ == "__main__":
    main()
