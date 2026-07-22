#!/usr/bin/env python3
"""Compute Table 1 style summaries, Kendall's W, and covariance-sign flips."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EVENTS = ["P1", "P2", "P3", "P4"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    values = sorted(values)
    n = len(values)
    mid = n // 2
    if n % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def average_ranks_desc(values: list[float]) -> list[float]:
    indexed = list(enumerate(values))
    indexed.sort(key=lambda item: item[1], reverse=True)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and abs(indexed[j][1] - indexed[i][1]) <= 1e-9:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def kendalls_w(rank_rows: list[list[float]]) -> float | None:
    if not rank_rows:
        return None
    m = len(rank_rows)
    n = len(rank_rows[0])
    item_totals = [sum(row[j] for row in rank_rows) for j in range(n)]
    mean_total = sum(item_totals) / n
    s_val = sum((total - mean_total) ** 2 for total in item_totals)
    tie_correction = 0.0
    for row in rank_rows:
        counts = Counter(row)
        tie_correction += sum(count ** 3 - count for count in counts.values() if count > 1)
    denom = (m**2) * (n**3 - n) - m * tie_correction
    if denom <= 0:
        return None
    return 12 * s_val / denom


def covariance(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def summarize_condition(rows: list[dict[str, str]]) -> dict[str, object]:
    by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_pianist: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_event[row["pause"]].append(row)
        by_pianist[row["pianist"]][row["pause"]] = row

    table = []
    peak_counts = Counter()
    rank_rows = []
    cov_signs = {}
    for pianist, event_map in sorted(by_pianist.items()):
        dl_values = [float(event_map[event]["d_l"]) for event in EVENTS]
        ds_values = [float(event_map[event]["d_s"]) for event in EVENTS]
        peak_event = max(EVENTS, key=lambda event: (float(event_map[event]["d_l"]), event))
        peak_counts[peak_event] += 1
        rank_rows.append(average_ranks_desc(dl_values))
        cov_val = covariance(ds_values, dl_values)
        cov_signs[pianist] = "compensating" if cov_val < 0 else "additive"

    median_rank_by_event = {}
    for event in EVENTS:
        event_ranks = []
        for pianist in sorted(by_pianist):
            dl_values = [float(by_pianist[pianist][ev]["d_l"]) for ev in EVENTS]
            event_ranks.append(average_ranks_desc(dl_values)[EVENTS.index(event)])
        median_rank_by_event[event] = median(event_ranks)

    for event in EVENTS:
        ds = [float(row["d_s"]) for row in by_event[event]]
        dl = [float(row["d_l"]) for row in by_event[event]]
        total = [float(row["T"]) for row in by_event[event]]
        table.append(
            {
                "pause": event,
                "mean_d_s": round(mean(ds), 3),
                "mean_d_l": round(mean(dl), 3),
                "mean_T": round(mean(total), 3),
                "median_d_l": round(median(dl), 3),
                "peak_n": peak_counts.get(event, 0),
                "median_rank": round(median_rank_by_event[event], 1),
            }
        )

    return {
        "table1": table,
        "kendalls_w": kendalls_w(rank_rows),
        "peak_counts": dict(peak_counts),
        "covariance_signs": cov_signs,
        "strategy_counts": dict(Counter(cov_signs.values())),
    }


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    rows = read_rows(base / "data/events.csv")
    source_rows = [row for row in rows if row["condition"] == "source"]
    peak_rows = [row for row in rows if row["condition"] == "peaknorm"]
    source_summary = summarize_condition(source_rows)
    peak_summary = summarize_condition(peak_rows)

    flips = {}
    for pianist, source_sign in source_summary["covariance_signs"].items():
        peak_sign = peak_summary["covariance_signs"].get(pianist)
        if peak_sign and peak_sign != source_sign:
            flips[pianist] = {"source": source_sign, "peaknorm": peak_sign}

    payload = {
        "source": source_summary,
        "peaknorm": peak_summary,
        "covariance_flip_count": len(flips),
        "covariance_flips": flips,
    }

    out_path = base / "data/analysis_summary.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
