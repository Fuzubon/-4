"""Lab 05 group 4: two report figures from raw interval/state CSV (no data edited).
Run from lab_05:  py -3 evidence/make_figures.py
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).parent / "comparison"
COLORS = {"B0": "#7a7a7a", "B1": "#c0392b", "B2": "#1f6fb2", "B3": "#e08a1e"}

def load(name):
    with open(BASE / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True, constrained_layout=True)
for c in ("B0", "B1", "B2", "B3"):
    rows = load(f"{c}_intervals.csv")
    t = [float(r["command_time_s"]) for r in rows]
    a1.step(t, [float(r["phi_rad"]) for r in rows], where="post", color=COLORS[c], lw=1.8, label=c)
    if c in ("B2", "B3"):
        a2.plot(t, [float(r["h_used"]) for r in rows], color=COLORS[c], lw=1.8, label=f"{c} H used")
for ax in (a1, a2):
    for x in (10, 20):
        ax.axvline(x, color="#999", ls=":", lw=1)
    ax.grid(alpha=.25)
a1.set_ylabel("phi command (rad)"); a1.legend(ncol=4, fontsize=8); a1.set_title("Figure 1: phi command by condition (stimulus on 10-20 s)")
a2.set_ylabel("H used"); a2.set_xlabel("command time (s)"); a2.legend(fontsize=8)
fig.savefig(Path(__file__).parent / "fig1_phi_command.png", dpi=150)

fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
for c in ("B0", "B1", "B2", "B3"):
    rows = load(f"{c}_states.csv")
    ax.plot([float(r["state_time_s"]) for r in rows], [float(r["body_x_m"]) for r in rows], color=COLORS[c], lw=1.8, label=c)
for x in (10, 20):
    ax.axvline(x, color="#999", ls=":", lw=1)
ax.set_xlabel("state time (s)"); ax.set_ylabel("body x (m)"); ax.grid(alpha=.25); ax.legend()
ax.set_title("Figure 2: kinematic body displacement (course model, not a real robot)")
fig.savefig(Path(__file__).parent / "fig2_body_x.png", dpi=150)
print("ok")
