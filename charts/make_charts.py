"""
make_charts.py - builds the 3 project charts from the CSVs that
sql/06_export_results.sql writes into results/.
Run from the project folder:  python3 charts/make_charts.py
Needs: pip install matplotlib
"""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# palette (validated: categorical slots 1-2 + neutral ink/chrome)
BLUE, ORANGE, GRAY_SERIES = "#2a78d6", "#eb6834", "#b9b7ae"
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SOURCE = ("Source: CFPB Consumer Complaint Database (downloaded 2026-09-30). Scope: 'Domestic (US) money transfer' "
          "+ 'Mobile or digital wallet' sub-products.")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})
comma = FuncFormatter(lambda v, _: f"{v:,.0f}")

def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def style(ax, grid_axis="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(grid_axis == "y")
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)

def titles(fig, title, subtitle):
    fig.text(0.02, 0.965, title, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.905, subtitle, fontsize=9.5, color=INK2, va="top")
    fig.text(0.02, 0.02, SOURCE, fontsize=7, color=MUTED)

# ---------- Chart 1: monthly volume ----------
rows = read("results/monthly_complaints.csv")
months = [r["month"] for r in rows]
vals = [int(r["complaints"]) for r in rows]
CAP = 6000
fig, ax = plt.subplots(figsize=(9, 4.2))
fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.16)
x = list(range(len(months)))
for start, end, label in [("2024-01", "2024-12", "2024 baseline\n872 / month"),
                          ("2026-01", "2026-09", "Jan–Sep 2026\n2,322 / month")]:
    i0, i1 = months.index(start), months.index(end)
    ax.axvspan(i0 - 0.5, i1 + 0.5, color=BLUE, alpha=0.07, linewidth=0)
    ax.text((i0 + i1) / 2, CAP * 0.93, label, ha="center", va="top", fontsize=8.5, color=INK2)
ax.plot(x, [min(v, CAP) for v in vals], color=BLUE, linewidth=2, solid_joinstyle="round", solid_capstyle="round")
pk = vals.index(max(vals))
ax.plot([pk], [CAP], marker="^", markersize=8, color=BLUE, markeredgecolor=SURFACE, markeredgewidth=2, clip_on=False)
ax.annotate(f"Jan 2025: {vals[pk]:,} (off scale)\nfiling wave after CFPB actions\nvs. Zelle & Cash App",
            xy=(pk, CAP), xytext=(pk - 0.8, CAP * 0.78), fontsize=8.5, color=INK2, va="top", ha="right")
oc = months.index("2025-10")
ax.text(oc, vals[oc] + 120, "Oct 2025:\n2nd wave", ha="center", va="bottom", fontsize=8, color=INK2)
ax.set_ylim(0, CAP)
ax.yaxis.set_major_formatter(comma)
ticks = [i for i, m in enumerate(months) if m.endswith("-01")]
ax.set_xticks(ticks, [months[i][:4] for i in ticks])
ax.set_xlim(-0.5, len(months) - 0.5)
style(ax)
titles(fig, "P2P & wallet complaints per month, Jan 2022 – Sep 2026",
       "Monthly volume is 2.7× higher in 2026 than 2024. 2025 is excluded from comparisons (event-driven filing waves).")
fig.text(0.02, 0.055, "Sep 2026 is likely incomplete: CFPB publishes some complaints with a delay.", fontsize=7, color=MUTED)
fig.savefig("charts/chart1_monthly_volume.png", dpi=200)
plt.close(fig)

# ---------- Chart 2: top issues, per month, 2024 vs 2026 ----------
short = {
    "Fraud or scam": "Fraud or scam",
    "Unauthorized transactions or other transaction problem": "Unauthorized transactions",
    "Trouble accessing funds in your mobile or digital wallet": "Trouble accessing funds",
    "Other transaction problem": "Other transaction problem",
    "Managing, opening, or closing your mobile wallet account": "Managing / closing account",
}
rows = [r for r in read("results/issues_2024_vs_2026.csv") if r["issue"] in short][:5]
rows = rows[::-1]  # biggest at top
labels = [short[r["issue"]] for r in rows]
a = [float(r["per_month_2024"]) for r in rows]
b = [float(r["per_month_2026"]) for r in rows]
fig, ax = plt.subplots(figsize=(9, 4.4))
fig.subplots_adjust(left=0.24, right=0.90, top=0.80, bottom=0.16)
h = 0.34
y = list(range(len(rows)))
ax.barh([i + h / 2 + 0.02 for i in y], a, height=h, color=GRAY_SERIES, label="2024 (per month)")
ax.barh([i - h / 2 - 0.02 for i in y], b, height=h, color=BLUE, label="Jan–Sep 2026 (per month)")
xmax = max(b) * 1.18
for i in y:
    ax.text(a[i] + 8, i + h / 2 + 0.02, f"{a[i]:,.0f}", va="center", fontsize=8, color=MUTED)
    ax.text(b[i] + 8, i - h / 2 - 0.02, f"{b[i]:,.0f}", va="center", fontsize=8.5, color=INK)
    g = b[i] / a[i]
    ax.text(xmax * 1.02, i, f"{g:.1f}×", va="center", ha="left", fontsize=10,
            fontweight="bold" if g >= 4 else "normal", color=INK if g >= 4 else INK2)
ax.text(xmax * 1.02, len(rows) - 0.45, "growth", fontsize=8, color=MUTED, ha="left")
ax.set_yticks(y, labels, color=INK, fontsize=9.5)
ax.set_xlim(0, xmax)
ax.xaxis.set_major_formatter(comma)
style(ax, grid_axis="x")
ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK2)
titles(fig, "Top 5 complaint issues: complaints per month, 2024 vs Jan–Sep 2026",
       "Fraud + unauthorized transactions = 54.7% of 2026 complaints. Unauthorized transactions grew fastest (4.1×).")
fig.savefig("charts/chart2_issues_growth.png", dpi=200)
plt.close(fig)

# ---------- Chart 3: outcomes by app ----------
order = ["PayPal + Venmo", "Banks & others", "Cash App (Block)", "Zelle network (EWS)"]
data = {r["app"]: r for r in read("results/outcomes_by_app_2026.csv")}
rows = [data[k] for k in order][::-1]
labels = [r["app"] for r in rows]
closed = [int(r["closed_complaints"]) for r in rows]
money = [100 * int(r["money_back"]) / int(r["closed_complaints"]) for r in rows]
other = [100 * int(r["other_relief"]) / int(r["closed_complaints"]) for r in rows]
fig, ax = plt.subplots(figsize=(9, 4.0))
fig.subplots_adjust(left=0.22, right=0.97, top=0.78, bottom=0.20)
y = list(range(len(rows)))
ax.barh(y, money, height=0.5, color=BLUE, label="Money back (monetary relief)")
ax.barh(y, other, left=[m + (0.3 if o > 0 else 0) for m, o in zip(money, other)], height=0.5,
        color=ORANGE, label="Other fix (non-monetary relief)")
for i, r in enumerate(rows):
    tot = money[i] + other[i]
    mb = int(r["money_back"])
    txt = (f"{tot:.1f}% any relief  ·  {money[i]:.1f}% money back" if tot >= 1
           else f"{mb:,} of {closed[i]:,} closed complaints got money back")
    ax.text(tot + 0.8, i, txt, va="center", fontsize=8.5, color=INK)
ax.set_yticks(y, [f"{l}\n{c:,} closed" for l, c in zip(labels, closed)], color=INK, fontsize=9)
ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
style(ax, grid_axis="x")
ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK2)
titles(fig, "How complaints ended, Jan–Sep 2026 (closed complaints, company-reported)",
       "Similar volume, different outcomes: PayPal + Venmo gave money back in 19.2% of cases; Cash App in 1 of 6,383.")
fig.text(0.02, 0.065, "Note: Zelle refunds are usually issued by the customer's bank (in 'Banks & others'), not by Early Warning Services.",
         fontsize=7, color=MUTED)
fig.savefig("charts/chart3_outcomes_by_app.png", dpi=200)
plt.close(fig)
print("saved 3 charts to charts/")

# ---------- Compact versions for the 1-page memo (titles come from the memo) ----------
def compact_axes(size=(5.4, 3.9)):
    fig, ax = plt.subplots(figsize=size)
    fig.set_facecolor("white"); ax.set_facecolor("white")
    return fig, ax

# memo chart A: issues per month
rows = [r for r in read("results/issues_2024_vs_2026.csv") if r["issue"] in short][:5][::-1]
labels = [short[r["issue"]].replace("Managing / closing account", "Managing account") for r in rows]
a = [float(r["per_month_2024"]) for r in rows]
b = [float(r["per_month_2026"]) for r in rows]
fig, ax = compact_axes()
fig.subplots_adjust(left=0.37, right=0.87, top=0.88, bottom=0.06)
h = 0.36
y = list(range(len(rows)))
ax.barh([i + h / 2 + 0.02 for i in y], a, height=h, color=GRAY_SERIES, label="2024")
ax.barh([i - h / 2 - 0.02 for i in y], b, height=h, color=BLUE, label="Jan–Sep 2026")
xmax = max(b) * 1.2
for i in y:
    ax.text(b[i] + 10, i - h / 2 - 0.02, f"{b[i]:,.0f}", va="center", fontsize=9, color=INK)
    ax.text(a[i] + 10, i + h / 2 + 0.02, f"{a[i]:,.0f}", va="center", fontsize=8.5, color=MUTED)
    g = b[i] / a[i]
    ax.text(xmax * 1.03, i, f"{g:.1f}×", va="center", fontsize=10.5,
            fontweight="bold" if g >= 4 else "normal", color=INK if g >= 4 else INK2)
ax.text(xmax * 1.03, len(rows) - 0.5, "growth", fontsize=8.5, color=MUTED)
ax.set_yticks(y, labels, color=INK, fontsize=10)
ax.set_xlim(0, xmax)
ax.set_xticks([])
style(ax, grid_axis="x")
ax.spines["bottom"].set_visible(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False, fontsize=9.5, labelcolor=INK2)
fig.savefig("charts/memo_issues.png", dpi=250, facecolor="white")
plt.close(fig)

# memo chart B: outcomes by app
rows = [data[k] for k in order][::-1]
closed = [int(r["closed_complaints"]) for r in rows]
money = [100 * int(r["money_back"]) / int(r["closed_complaints"]) for r in rows]
other = [100 * int(r["other_relief"]) / int(r["closed_complaints"]) for r in rows]
fig, ax = compact_axes()
fig.subplots_adjust(left=0.27, right=0.97, top=0.88, bottom=0.06)
y = list(range(len(rows)))
ax.barh(y, money, height=0.5, color=BLUE, label="Money back")
ax.barh(y, other, left=[m + (0.4 if o > 0 else 0) for m, o in zip(money, other)], height=0.5,
        color=ORANGE, label="Other fix")
for i, r in enumerate(rows):
    tot = money[i] + other[i]
    txt = (f"{tot:.1f}% relief\n({money[i]:.1f}% money back)" if tot >= 1
           else f"{int(r['money_back']):,} of {closed[i]:,}\ngot money back")
    ax.text(tot + 1.2, i, txt, va="center", fontsize=9, color=INK, linespacing=1.15)
short_app = {"Cash App (Block)": "Cash App", "Zelle network (EWS)": "Zelle network",
             "PayPal + Venmo": "PayPal + Venmo", "Banks & others": "Banks & others"}
ax.set_yticks(y, [f"{short_app[r['app']]}\n{c:,} closed" for r, c in zip(rows, closed)], color=INK, fontsize=9.5)
ax.set_xlim(0, 75)
ax.set_xticks([])
style(ax, grid_axis="x")
ax.spines["bottom"].set_visible(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, frameon=False, fontsize=9.5, labelcolor=INK2)
fig.savefig("charts/memo_outcomes.png", dpi=250, facecolor="white")
plt.close(fig)
from PIL import Image as _PIL
for _p in ("charts/memo_issues.png", "charts/memo_outcomes.png"):
    _PIL.open(_p).convert("RGB").save(_p)   # flatten alpha so PDF viewers show pure white
print("saved memo chart versions")
