"""
make_memo.py - builds the 1-page insight memo PDF.
Every number below comes from the SQL outputs in sql/01-06 (see README).
Run from the project folder:  python3 memo/make_memo.py
Needs: pip install reportlab
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image)

AUTHOR = "Khushi Jha"
GITHUB = "github.com/khushi-jha02/cfpb-payments-analysis"
INK, INK2, MUTED, RULE, BLUE, WASH = (HexColor(c) for c in
    ["#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#2a78d6", "#eef4fc"])

def S(name, size, lead, color=INK, bold=False, **kw):
    return ParagraphStyle(name, fontName="Helvetica-Bold" if bold else "Helvetica",
                          fontSize=size, leading=lead, textColor=color, **kw)
title = S("t", 15.5, 18.5, bold=True)
sub   = S("s", 8.3, 10.5, INK2)
h     = S("h", 9, 11, BLUE, bold=True, spaceBefore=6, spaceAfter=2)
body  = S("b", 8.6, 11.2)
cell  = S("c", 8.1, 10.2)
cellb = S("cb", 8.1, 10.2, bold=True)
small = S("sm", 7.4, 9.2, INK2)

doc = SimpleDocTemplate("memo/cfpb_p2p_insight_memo.pdf", pagesize=letter,
                        leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=26,
                        title="Where P2P Payment Apps Break", author=AUTHOR)
W = letter[0] - 72
story = []

story += [Paragraph("Where P2P Payment Apps Break: Evidence from 124,087 CFPB Complaints", title),
          Spacer(1, 3),
          Paragraph(f"{AUTHOR} &nbsp;·&nbsp; September 30, 2026 &nbsp;·&nbsp; Cash App, Zelle, PayPal/Venmo and banks "
                    "&nbsp;·&nbsp; SQL (DuckDB) analysis of public CFPB data", sub),
          Spacer(1, 6)]

bl = Table([[Paragraph(
    "<b>Bottom line:</b> More than half of P2P and wallet complaints are about money leaving an account without the "
    "customer's real consent, unauthorized transactions are the fastest-growing problem, and outcomes differ sharply by "
    "app. The biggest product opportunity is <b>stopping bad payments before they happen and resolving them inside the app</b>.",
    body)]], colWidths=[W])
bl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WASH), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LINEBEFORE", (0, 0), (0, -1), 2.5, BLUE)]))
story += [bl]

story += [Paragraph("Data &amp; method", h), Paragraph(
    "CFPB Consumer Complaint Database, product <i>Money transfer, virtual currency, or money service</i>, sub-products "
    "<i>Domestic (US) money transfer</i> and <i>Mobile or digital wallet</i>: 124,087 complaints, Jan 2022 to Sep 2026. "
    "Main comparison: <b>2024</b> (10,461 complaints) vs <b>Jan–Sep 2026</b> (20,894), per month so 12 and 9 months compare "
    "fairly. <b>2025 is excluded</b>: January 2025 alone had 48,238 complaints, 87.2% under one vague issue and 95.9% against "
    "Cash App or Zelle, a filing wave that coincides with CFPB actions against Zelle's operator and banks (Dec 20, 2024) and "
    "Block (Jan 16, 2025). It took until about Aug 2025 to return to normal.", body)]

story += [Paragraph("Three insights and what I would build", h)]
rows = [[Paragraph("Insight (from the data)", cellb), Paragraph("Recommendation", cellb),
         Paragraph("Success metric", cellb)],
        [Paragraph("<b>1. Consent is the core failure.</b> 54.7% of Jan–Sep 2026 complaints (11,428 of 20,894) were fraud/scams "
                   "or unauthorized transactions, vs 53.6% in 2024. Stable share = structural problem, not a blip.", cell),
         Paragraph("<b>Risk-based \"pause &amp; confirm.\"</b> For first-time recipients, unusual amounts or new devices, show a "
                   "scam-specific warning and require confirmation before money leaves.", cell),
         Paragraph("Fraud/scam complaints per 10K active users; scam loss rate; warning abandon rate", cell)],
        [Paragraph("<b>2. Unauthorized transactions grow fastest.</b> 138 to 571 complaints/month (4.1×) vs 2.7× for all "
                   "complaints (872 to 2,322/month); share rose from 15.9% to 24.6%. Account access issues also up 2.9–3.2×.", cell),
         Paragraph("<b>One-tap \"I didn't make this.\"</b> Lock account and open a dispute in one flow, with real-time "
                   "transaction alerts and step-up verification on new devices.", cell),
         Paragraph("Unauthorized-transaction complaints/month; time from alert to lock", cell)],
        [Paragraph("<b>3. Similar volume, very different outcomes.</b> Cash App (6,490) and PayPal + Venmo (6,341) had similar "
                   "Jan–Sep 2026 volume. PayPal + Venmo reported money back in 19.2% of closed complaints (42.6% any relief); "
                   "Cash App in 1 of 6,383.", cell),
         Paragraph("<b>In-app dispute tracker.</b> Show status, timeline, decision reason and appeal path, so customers get "
                   "answers in the app instead of escalating to a federal regulator.", cell),
         Paragraph("Share of disputes escalated to CFPB; relief rate; time to resolution", cell)]]
t = Table(rows, colWidths=[W * 0.44, W * 0.36, W * 0.20])
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.6, RULE),
                       ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                       ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story += [t, Spacer(1, 8)]

cw = (W - 14) / 2
cap = S("cap", 8, 10, INK, bold=True)
capn = S("capn", 7, 8.6, MUTED)
img = lambda p: Image(p, width=cw, height=cw * 3.9 / 5.4)
charts = Table([[Paragraph("Complaints per month, top 5 issues: 2024 vs Jan–Sep 2026", cap),
                 Paragraph("How closed complaints ended, Jan–Sep 2026 (company-reported)", cap)],
                [img("charts/memo_issues.png"), img("charts/memo_outcomes.png")],
                [Paragraph("Insights 1 and 2. Per-month rates make 12 vs 9 months comparable.", capn),
                 Paragraph("Insight 3. Zelle refunds are usually issued by banks (in \"Banks &amp; others\").", capn)]],
               colWidths=[cw + 7, cw + 7])
charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
story += [charts, Spacer(1, 2)]

story += [Paragraph("Caveats", h), Paragraph(
    "CFPB complaints are escalations by a self-selected group, not all users, so I rely on shares and comparisons more than "
    "raw volume. Complaint growth may partly reflect more awareness of the CFPB. Outcomes are company-reported. Venmo is filed "
    "under PayPal Holdings and cannot be separated. Zelle's operator reports 0% relief because refunds usually come from the "
    "customer's bank (in \"Banks &amp; others\": 7.1% money back). Sep 2026 is likely incomplete due to publication lag.", small),
    Spacer(1, 5),
    Paragraph(f"SQL (6 queries), data snapshot and charts: {GITHUB}", small)]

doc.build(story)
print("saved memo/cfpb_p2p_insight_memo.pdf")
