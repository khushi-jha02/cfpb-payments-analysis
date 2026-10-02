"""
Build the 1-page insight memo PDF (memo/cfpb_p2p_insight_memo.pdf).
Every number comes from the SQL outputs in sql/01 to sql/06 (see README).
Run from the project folder:  python3 memo/make_memo.py
Requires: pip install reportlab
"""
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AUTHOR = "Khushi Jha"
GITHUB = "github.com/khushi-jha02/cfpb-payments-analysis"

INK, INK2, MUTED, RULE, BLUE, WASH = (HexColor(c) for c in
    ["#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#2a78d6", "#eef4fc"])


def style(name, size, leading, color=INK, bold=False):
    return ParagraphStyle(name, fontName="Helvetica-Bold" if bold else "Helvetica",
                          fontSize=size, leading=leading, textColor=color)


TITLE = style("title", 15.5, 18.5, bold=True)
SUB = style("sub", 8.3, 10.5, INK2)
HEAD = style("head", 9, 11, BLUE, bold=True)
BODY = style("body", 8.6, 11.2)
CELL = style("cell", 8.1, 10.2)
CELL_HEAD = style("cellhead", 8.1, 10.2, bold=True)
CAPTION = style("caption", 8, 10, bold=True)
NOTE = style("note", 7, 8.6, MUTED)
SMALL = style("small", 7.4, 9.2, INK2)

doc = SimpleDocTemplate("memo/cfpb_p2p_insight_memo.pdf", pagesize=letter,
                        leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=26,
                        title="Where P2P Payment Apps Break", author=AUTHOR)
W = letter[0] - 72
story = []


def heading(text):
    story.extend([Spacer(1, 6), Paragraph(text, HEAD), Spacer(1, 2)])


# ---- title ----
story += [
    Paragraph("Where P2P Payment Apps Break: An Analysis of 124,087 CFPB Complaints", TITLE),
    Spacer(1, 3),
    Paragraph(f"{AUTHOR} | September 30, 2026 | SQL analysis of public CFPB complaint data", SUB),
    Spacer(1, 6),
]

# ---- bottom line ----
box = Table([[Paragraph(
    "Bottom line: More than half of complaints about P2P apps and digital wallets are about money that "
    "left an account without the customer's real consent. Unauthorized transactions are the fastest growing "
    "problem, and how complaints end varies a lot by app. The biggest opportunity is to stop bad payments "
    "before they happen and to resolve disputes inside the app.", BODY)]], colWidths=[W])
box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), WASH), ("LINEBEFORE", (0, 0), (0, -1), 2.5, BLUE),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(box)

# ---- data and method ----
heading("Data and method")
story.append(Paragraph(
    "I used the CFPB Consumer Complaint Database and kept two sub-products: domestic money transfers and "
    "mobile or digital wallets. That gave 124,087 complaints from January 2022 to September 2026. I compared "
    "2024 (10,461 complaints) with January to September 2026 (20,894 complaints), using complaints per month "
    "so the two periods are comparable. I left 2025 out of the comparison. January 2025 alone had 48,238 "
    "complaints, 87.2% of them under one vague issue and 95.9% against Cash App or Zelle. This wave followed "
    "CFPB actions against Zelle's operator and three banks (Dec 20, 2024) and against Block (Jan 16, 2025), "
    "and complaint patterns did not return to normal until about August 2025.", BODY))

# ---- insights table ----
heading("Three insights and what I would build")
rows = [
    ["What the data shows", "What I would build", "How to measure it"],
    ["1. Fraud and unauthorized transactions are the main problem. They made up 54.7% of complaints in "
     "Jan to Sep 2026 (11,428 of 20,894), about the same as 53.6% in 2024.",
     "A pause and confirm step before risky payments, such as a first payment to a new person, an unusual "
     "amount or a new device, with a clear scam warning.",
     "Fraud and scam complaints per 10K active users; scam loss rate"],
    ["2. Unauthorized transactions are growing fastest. They went from 138 to 571 complaints per month "
     "(4.1x), while all complaints grew 2.7x (872 to 2,322 per month).",
     "One tap to lock the account and open a dispute, with real time alerts and extra verification "
     "on new devices.",
     "Unauthorized transaction complaints per month; time from alert to lock"],
    ["3. Similar volume, very different outcomes. Cash App (6,490) and PayPal plus Venmo (6,341) had similar "
     "complaint volume in Jan to Sep 2026. PayPal plus Venmo gave money back in 19.2% of closed complaints. "
     "Cash App did in 1 of 6,383.",
     "An in-app dispute tracker that shows status, timeline, the reason for the decision and how to appeal, "
     "so users do not need to go to a regulator.",
     "Share of disputes escalated to the CFPB; relief rate; time to resolve"],
]
table = Table([[Paragraph(c, CELL_HEAD if i == 0 else CELL) for c in r] for i, r in enumerate(rows)],
              colWidths=[W * 0.44, W * 0.36, W * 0.20])
table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.6, RULE),
    ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [table, Spacer(1, 8)]

# ---- charts ----
cw = (W - 14) / 2
img = lambda path: Image(path, width=cw, height=cw * 3.9 / 5.4)
charts = Table([
    [Paragraph("Complaints per month, top 5 issues: 2024 vs Jan to Sep 2026", CAPTION),
     Paragraph("How closed complaints ended, Jan to Sep 2026", CAPTION)],
    [img("charts/memo_issues.png"), img("charts/memo_outcomes.png")],
    [Paragraph("Insights 1 and 2.", NOTE),
     Paragraph("Insight 3. Outcomes as reported by companies. Zelle refunds usually come from the "
               "customer's bank, which is counted in Banks & others.", NOTE)],
], colWidths=[cw + 7, cw + 7])
charts.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
]))
story += [charts, Spacer(1, 2)]

# ---- caveats ----
heading("Caveats")
story += [
    Paragraph(
        "CFPB complaints come from people who chose to escalate, not from all users, so I focus on shares and "
        "comparisons rather than raw volume. Some of the growth may come from more people knowing about the CFPB. "
        "Outcomes are reported by the companies. Venmo is filed under PayPal and cannot be separated. Zelle's "
        "operator shows 0% relief because refunds usually come from banks (7.1% money back in the Banks & others "
        "group). September 2026 is likely incomplete because some complaints are published late.", SMALL),
    Spacer(1, 5),
    Paragraph(f"SQL, data and charts: {GITHUB}", SMALL),
]

doc.build(story)
print("Saved memo/cfpb_p2p_insight_memo.pdf")
