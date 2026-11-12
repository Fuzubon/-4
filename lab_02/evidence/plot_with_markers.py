"""Lab 02 group 4: plot one trial and mark physical crossing + first correct response.

Usage (from lab_02):
    py -3 evidence/plot_with_markers.py evidence/student_comparison/trials/C1_n0.01_d000_r01.csv --out evidence/plots/C1_r01.png

- physical crossing  = เวลาที่ true_distance_m ข้าม 0.35 m (ขาเข้า/ขาออก)
- first correct      = เวลาแรกหลัง crossing ที่ state เท่ากับ expected_state
ใช้ข้อมูลจาก raw CSV เท่านั้น ไม่แก้ค่าใน CSV
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

THRESHOLD_M = 0.35


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def fnum(value: str) -> float | None:
    return None if value == "" else float(value)


def crossings(rows: list[dict[str, str]]) -> list[tuple[float, str]]:
    out = []
    for prev, cur in zip(rows, rows[1:]):
        a, b = float(prev["true_distance_m"]), float(cur["true_distance_m"])
        if a >= THRESHOLD_M > b:
            out.append((float(cur["time_s"]), "NEAR"))
        elif a < THRESHOLD_M <= b:
            out.append((float(cur["time_s"]), "FAR"))
    return out


def first_correct(rows: list[dict[str, str]], t_cross: float, target: str) -> float | None:
    for row in rows:
        if float(row["time_s"]) >= t_cross and row["state"] == target:
            return float(row["time_s"])
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = load(args.csv_path)
    t = [float(r["time_s"]) for r in rows]
    true_d = [float(r["true_distance_m"]) for r in rows]
    raw_d = [fnum(r["raw_distance_m"]) for r in rows]
    filt_d = [fnum(r["filtered_distance_m"]) for r in rows]
    cmd = [float(r["command"]) for r in rows]
    state = [1 if r["state"] == "NEAR" else 0 for r in rows]
    cond = rows[0]["condition"]

    fig, (ax_d, ax_c) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, constrained_layout=True)
    ax_d.plot(t, true_d, color="#161616", linewidth=2, label="true distance")
    ax_d.plot(t, raw_d, color="#A7ADB1", linewidth=1, alpha=0.8, label="raw")
    if any(v is not None for v in filt_d):
        ax_d.plot(t, filt_d, color="#147A8C", linewidth=2, label="filtered")
    ax_d.axhline(THRESHOLD_M, color="#B84A4A", linestyle="--", linewidth=1.5, label="T = 0.35 m")
    if cond == "C2":
        ax_d.axhline(0.32, color="#147A8C", linestyle=":", linewidth=1.2, label="T_enter 0.32")
        ax_d.axhline(0.38, color="#C17824", linestyle=":", linewidth=1.2, label="T_exit 0.38")
    ax_d.set_ylabel("distance (m)")
    ax_d.grid(True, alpha=0.25)

    ax_c.plot(t, cmd, color="#C17824", linewidth=2, label="command")
    ax_c.step(t, state, where="post", color="#147A8C", linewidth=1.5, label="state NEAR=1")
    ax_c.set_xlabel("time (s)")
    ax_c.set_ylabel("command / state")
    ax_c.grid(True, alpha=0.25)

    lines = []
    for i, (tc, target) in enumerate(crossings(rows)):
        tf = first_correct(rows, tc, target)
        for ax in (ax_d, ax_c):
            ax.axvline(tc, color="#6B4FA0", linestyle="--", linewidth=1.2,
                       label="physical crossing" if (i == 0 and ax is ax_d) else None)
            if tf is not None:
                ax.axvline(tf, color="#2E8B57", linestyle="-", linewidth=1.2,
                           label="first correct response" if (i == 0 and ax is ax_d) else None)
        txt = f"{target}: cross {tc:.2f} s, correct {tf:.2f} s, latency {tf - tc:.2f} s" if tf is not None \
            else f"{target}: cross {tc:.2f} s, no correct response"
        lines.append(txt)
    ax_d.legend(loc="upper right", ncol=3, fontsize=8)
    ax_c.legend(loc="upper right", fontsize=8)
    ax_c.text(0.01, 0.04, "\n".join(lines), transform=ax_c.transAxes, fontsize=8,
              bbox=dict(facecolor="white", alpha=0.85, edgecolor="#cccccc"))
    fig.suptitle(f"{rows[0]['trial_id']} | {cond} | sigma={rows[0]['noise_sigma_m']} m | delay={rows[0]['delay_ms']} ms")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
