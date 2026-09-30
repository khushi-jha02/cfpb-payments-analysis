"""
Build the project charts from the CSVs written by sql/06_export_results.sql.

Outputs (in charts/):
    chart1_monthly_volume.png    complaints per month, Jan 2022 - Sep 2026
    chart2_issues_growth.png     top 5 issues per month, 2024 vs Jan-Sep 2026
    chart3_outcomes_by_app.png   how closed complaints ended, by app (2026)
    memo_issues.png, memo_outcomes.png   compact versions for the 1-page memo

Run from the project folder:  python3 charts/make_charts.py
Requires: pip install matplotlib pillow
"""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from PIL import Image

# ---- style ---------------------------------------------------------------
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#b9b7ae"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
SOURCE = ("Source: CFPB Consumer Complaint Database (downloaded 2026-09-30). "
          "Scope: 'Domestic (US) money transfer' + 'Mobile or digital wallet' sub-products.")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})
COMMA = FuncFormatter(lambda v, _: f"{v:,.0f}")

# Issue names are long in the CFPB data, so we shorten them for labels.
SHORT_ISSUE = {
    "Fraud or scam": "Fraud or scam",
    "Unauthorized transactions or other transaction problem": "Unauthorized transactions",
    "Trouble accessing funds in your mobile or digital wallet": "Trouble accessing funds",
    "Other transaction problem": "Other transaction problem",
    "Managing, opening, or closing your mobile wallet account": "Managing account",
}
APP_ORDER = ["PayPal + Venmo", "Banks & others", "Cash App (Block)", "Zelle network (EWS)"]


# ---- helpers -------------------------------------------------------------
def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def style_axes(ax, grid_axis="y"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(grid_axis == "y")
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def add_titles(fig, title, subtitle, note=None):
    fig.text(0.02, 0.965, title, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.905, subtitle, fontsize=9.5, color=INK2, va="top")
    if note:
        fig.text(0.02, 0.055, note, fontsize=7, color=MUTED)
    fig.text(0.02, 0.02, SOURCE, fontsize=7, color=MUTED)


def save(fig, path, dpi=200, white=False):
    fig.savefig(path, dpi=dpi, facecolor="white" if white else SURFACE)
    plt.close(fig)
    if white:  # flatten transparency so PDF viewers show pure white
        Image.open(path).convert("RGB").save(path)


# ---- load data -----------------------------------------------------------
monthly = read_csv("results/monthly_complaints.csv")
issues = [r for r in read_csv("results/issues_2024_vs_2026.csv") if r["issue"] in SHORT_ISSUE]
outcomes = {r["app"]: r for r in read_csv("results/outcomes_by_app_2026.csv")}

months = [r["month"] for r in monthly]
counts = [int(r["complaints"]) for r in monthly]
per_month_2024 = sum(c for m, c in zip(months, counts) if m.startswith("2024")) / 12
per_month_2026 = sum(c for m, c in zip(months, counts) if m.startswith("2026")) / 9

top5 = issues[:5][::-1]                      # CSV is sorted largest first; plot largest at top
issue_labels = [SHORT_ISSUE[r["issue"]] for r in top5]
issue_2024 = [float(r["per_month_2024"]) for r in top5]
issue_2026 = [float(r["per_month_2026"]) for r in top5]
fraud_unauth_share = sum(float(r["share_2026"]) for r in issues
                         if r["issue"] in ("Fraud or scam",
                                           "Unauthorized transactions or other transaction problem"))

apps = [outcomes[a] for a in APP_ORDER][::-1]
closed = [int(r["closed_complaints"]) for r in apps]
money_pct = [100 * int(r["money_back"]) / n for r, n in zip(apps, closed)]
other_pct = [100 * int(r["other_relief"]) / n for r, n in zip(apps, closed)]
paypal, cashapp = outcomes["PayPal + Venmo"], outcomes["Cash App (Block)"]


# ---- chart 1: monthly volume ----------------------------------------------
def chart_monthly_volume():
    cap = 6000                                # y-axis cap so normal months stay readable
    fig, ax = plt.subplots(figsize=(9, 4.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.16)
    x = range(len(months))

    for start, end, label in [("2024-01", "2024-12", f"2024 baseline\n{per_month_2024:,.0f} / month"),
                              ("2026-01", "2026-09", f"Jan–Sep 2026\n{per_month_2026:,.0f} / month")]:
        i0, i1 = months.index(start), months.index(end)
        ax.axvspan(i0 - 0.5, i1 + 0.5, color=BLUE, alpha=0.07, linewidth=0)
        ax.text((i0 + i1) / 2, cap * 0.93, label, ha="center", va="top", fontsize=8.5, color=INK2)

    ax.plot(x, [min(c, cap) for c in counts], color=BLUE, linewidth=2,
            solid_joinstyle="round", solid_capstyle="round")

    peak = counts.index(max(counts))
    ax.plot([peak], [cap], marker="^", markersize=8, color=BLUE,
            markeredgecolor=SURFACE, markeredgewidth=2, clip_on=False)
    ax.annotate(f"{months[peak]}: {counts[peak]:,} (off scale)\nfiling wave after CFPB actions\nvs. Zelle & Cash App",
                xy=(peak, cap), xytext=(peak - 0.8, cap * 0.78),
                fontsize=8.5, color=INK2, va="top", ha="right")
    oct25 = months.index("2025-10")
    ax.text(oct25, counts[oct25] + 120, "Oct 2025:\n2nd wave", ha="center", va="bottom", fontsize=8, color=INK2)

    ax.set_ylim(0, cap)
    ax.yaxis.set_major_formatter(COMMA)
    ticks = [i for i, m in enumerate(months) if m.endswith("-01")]
    ax.set_xticks(ticks, [months[i][:4] for i in ticks])
    ax.set_xlim(-0.5, len(months) - 0.5)
    style_axes(ax)
    add_titles(fig, "P2P & wallet complaints per month, Jan 2022 – Sep 2026",
               f"Monthly volume is {per_month_2026 / per_month_2024:.1f}× higher in 2026 than 2024. "
               "2025 is excluded from comparisons (event-driven filing waves).",
               note="Sep 2026 is likely incomplete: CFPB publishes some complaints with a delay.")
    save(fig, "charts/chart1_monthly_volume.png")


# ---- chart 2: top issues, 2024 vs 2026 --------------------------------------
def draw_issue_bars(ax, compact):
    h = 0.36 if compact else 0.34
    y = range(len(top5))
    ax.barh([i + h / 2 + 0.02 for i in y], issue_2024, height=h, color=GRAY,
            label="2024" if compact else "2024 (per month)")
    ax.barh([i - h / 2 - 0.02 for i in y], issue_2026, height=h, color=BLUE,
            label="Jan–Sep 2026" if compact else "Jan–Sep 2026 (per month)")
    xmax = max(issue_2026) * (1.2 if compact else 1.18)
    for i in y:
        ax.text(issue_2024[i] + 8, i + h / 2 + 0.02, f"{issue_2024[i]:,.0f}", va="center", fontsize=8, color=MUTED)
        ax.text(issue_2026[i] + 8, i - h / 2 - 0.02, f"{issue_2026[i]:,.0f}", va="center", fontsize=8.5, color=INK)
        growth = issue_2026[i] / issue_2024[i]
        ax.text(xmax * 1.02, i, f"{growth:.1f}×", va="center", ha="left", fontsize=10,
                fontweight="bold" if growth >= 4 else "normal", color=INK if growth >= 4 else INK2)
    ax.text(xmax * 1.02, len(top5) - 0.45, "growth", fontsize=8, color=MUTED, ha="left")
    ax.set_yticks(list(y), issue_labels, color=INK, fontsize=10 if compact else 9.5)
    ax.set_xlim(0, xmax)
    style_axes(ax, grid_axis="x")


def chart_issues():
    fig, ax = plt.subplots(figsize=(9, 4.4))
    fig.subplots_adjust(left=0.24, right=0.90, top=0.80, bottom=0.16)
    draw_issue_bars(ax, compact=False)
    ax.xaxis.set_major_formatter(COMMA)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK2)
    add_titles(fig, "Top 5 complaint issues: complaints per month, 2024 vs Jan–Sep 2026",
               f"Fraud + unauthorized transactions = {fraud_unauth_share:.1f}% of 2026 complaints. "
               "Unauthorized transactions grew fastest.")
    save(fig, "charts/chart2_issues_growth.png")


# ---- chart 3: outcomes by app -----------------------------------------------
def draw_outcome_bars(ax, compact):
    y = range(len(apps))
    ax.barh(y, money_pct, height=0.5, color=BLUE,
            label="Money back" if compact else "Money back (monetary relief)")
    gap = 0.4 if compact else 0.3              # small gap between the two segments
    ax.barh(y, other_pct, left=[m + (gap if o > 0 else 0) for m, o in zip(money_pct, other_pct)],
            height=0.5, color=ORANGE, label="Other fix" if compact else "Other fix (non-monetary relief)")
    for i, r in enumerate(apps):
        total = money_pct[i] + other_pct[i]
        if total >= 1:
            if compact:
                text = f"{total:.1f}% relief\n({money_pct[i]:.1f}% money back)"
            else:
                text = f"{total:.1f}% any relief  ·  {money_pct[i]:.1f}% money back"
        else:
            sep = "\n" if compact else " closed complaints "
            text = f"{int(r['money_back']):,} of {closed[i]:,}{sep}got money back"
        ax.text(total + 1, i, text, va="center", fontsize=9 if compact else 8.5, color=INK, linespacing=1.15)
    names = [r["app"].replace(" (Block)", "").replace(" (EWS)", "") if compact else r["app"] for r in apps]
    ax.set_yticks(list(y), [f"{n}\n{c:,} closed" for n, c in zip(names, closed)],
                  color=INK, fontsize=9.5 if compact else 9)
    style_axes(ax, grid_axis="x")


def chart_outcomes():
    fig, ax = plt.subplots(figsize=(9, 4.0))
    fig.subplots_adjust(left=0.22, right=0.97, top=0.78, bottom=0.20)
    draw_outcome_bars(ax, compact=False)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK2)
    add_titles(fig, "How complaints ended, Jan–Sep 2026 (closed complaints, company-reported)",
               f"Similar volume, different outcomes: PayPal + Venmo gave money back in {paypal['pct_money_back']}% "
               f"of cases; Cash App in {int(cashapp['money_back']):,} of {int(cashapp['closed_complaints']):,}.",
               note="Note: Zelle refunds are usually issued by the customer's bank (in 'Banks & others'), "
                    "not by Early Warning Services.")
    save(fig, "charts/chart3_outcomes_by_app.png")


# ---- compact versions for the memo (titles come from the memo itself) --------
def memo_charts():
    for name, draw, left, xlim, legend_x in [("memo_issues.png", draw_issue_bars, 0.37, None, 0.45),
                                             ("memo_outcomes.png", draw_outcome_bars, 0.27, 75, 0.40)]:
        fig, ax = plt.subplots(figsize=(5.4, 3.9))
        fig.set_facecolor("white")
        ax.set_facecolor("white")
        fig.subplots_adjust(left=left, right=0.87 if xlim is None else 0.97, top=0.88, bottom=0.06)
        draw(ax, compact=True)
        if xlim:
            ax.set_xlim(0, xlim)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.legend(loc="lower center", bbox_to_anchor=(legend_x, 1.0), ncol=2,
                  frameon=False, fontsize=9.5, labelcolor=INK2)
        save(fig, f"charts/{name}", dpi=250, white=True)


if __name__ == "__main__":
    chart_monthly_volume()
    chart_issues()
    chart_outcomes()
    memo_charts()
    print("Saved 5 charts to charts/")
