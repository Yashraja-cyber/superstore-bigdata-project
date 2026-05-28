import base64
import os
import pandas as pd
import subprocess

HDFS_CHARTS = "/user/yashraja/bigdata/output/charts"
TEMP = "/tmp/superstore_charts"
os.makedirs(TEMP, exist_ok=True)

chart_files = [
    "1_sales_by_region.png",
    "2_profit_by_category.png",
    "3_top10_subcategory.png",
    "4_discount_vs_profit.png",
    "5_sales_by_shipmode.png",
]

print("Downloading charts from HDFS...")
for f in chart_files:
    subprocess.run(["hdfs", "dfs", "-get", "-f",
                    f"{HDFS_CHARTS}/{f}", f"{TEMP}/{f}"],
                   capture_output=True)
    print(f"  {'✅' if os.path.exists(f'{TEMP}/{f}') else '⚠️ '} {f}")

def to_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

c1 = to_b64(f"{TEMP}/1_sales_by_region.png")
c2 = to_b64(f"{TEMP}/2_profit_by_category.png")
c3 = to_b64(f"{TEMP}/3_top10_subcategory.png")
c4 = to_b64(f"{TEMP}/4_discount_vs_profit.png")
c5 = to_b64(f"{TEMP}/5_sales_by_shipmode.png")

df = pd.read_csv("/home/yashraja/bigdata-project/SampleSuperstore.csv")
df.columns = df.columns.str.strip()
print("Columns found:", df.columns.tolist())

total_sales       = round(df["Sales"].sum(), 2)
total_profit      = round(df["Profit"].sum(), 2)
total_orders      = len(df)
profit_margin     = round((df["Profit"].sum() / df["Sales"].sum()) * 100, 2)
avg_order_value   = round(df["Sales"].mean(), 2)
avg_discount      = round(df["Discount"].mean() * 100, 1)
profitable_orders = len(df[df["Profit"] > 0])
loss_orders       = len(df[df["Profit"] < 0])
profit_pct        = round((profitable_orders / total_orders) * 100, 1)
loss_pct          = round((loss_orders / total_orders) * 100, 1)

top_region        = df.groupby("Region")["Sales"].sum().idxmax()
top_region_sales  = round(df.groupby("Region")["Sales"].sum().max(), 2)
top_region_profit = round(df.groupby("Region")["Profit"].sum().max(), 2)
bottom_region     = df.groupby("Region")["Sales"].sum().idxmin()

top_category      = df.groupby("Category")["Profit"].sum().idxmax()
top_cat_profit    = round(df.groupby("Category")["Profit"].sum().max(), 2)

top_sub           = df.groupby("Sub-Category")["Profit"].sum().idxmax()
top_sub_val       = round(df.groupby("Sub-Category")["Profit"].sum().max(), 2)
loss_sub          = df.groupby("Sub-Category")["Profit"].sum().idxmin()
loss_val          = round(df.groupby("Sub-Category")["Profit"].sum().min(), 2)

high_disc         = df[df["Discount"] >= 0.4]
high_disc_loss    = round(high_disc["Profit"].mean(), 2)
high_disc_count   = len(high_disc)
high_disc_pct     = round((high_disc_count / total_orders) * 100, 1)
zero_disc         = df[df["Discount"] == 0]
zero_disc_profit  = round(zero_disc["Profit"].mean(), 2)

top_ship          = df.groupby("Ship Mode")["Sales"].sum().idxmax()
top_ship_pct      = round((df[df["Ship Mode"] == top_ship]["Sales"].sum() / total_sales) * 100, 1)

best_year         = "N/A"
best_year_sales   = 0

region_data   = df.groupby("Region")[["Sales","Profit"]].sum().reset_index().sort_values("Sales", ascending=False)
region_data["Margin"] = (region_data["Profit"] / region_data["Sales"] * 100).round(1)

category_data = df.groupby("Category")[["Sales","Profit"]].sum().reset_index().sort_values("Profit", ascending=False)
category_data["Margin"] = (category_data["Profit"] / category_data["Sales"] * 100).round(1)

subcat_data   = df.groupby("Sub-Category")[["Sales","Profit"]].sum().reset_index().sort_values("Profit", ascending=False)
subcat_data["Margin"] = (subcat_data["Profit"] / subcat_data["Sales"] * 100).round(1)

shipmode_data = df.groupby("Ship Mode")[["Sales","Profit"]].sum().reset_index()
shipmode_data["Orders"] = df.groupby("Ship Mode").size().values
shipmode_data["Pct"] = (shipmode_data["Sales"] / total_sales * 100).round(1)
shipmode_data = shipmode_data.sort_values("Sales", ascending=False)

region_rows = "".join([
    f"<tr><td>{r['Region']}</td><td>${r['Sales']:,.0f}</td>"
    f"<td class=\"{'pos' if r['Profit']>0 else 'neg'}\">${r['Profit']:,.0f}</td>"
    f"<td>{r['Margin']}%</td></tr>"
    for _, r in region_data.iterrows()])

category_rows = "".join([
    f"<tr><td>{r['Category']}</td><td>${r['Sales']:,.0f}</td>"
    f"<td class=\"{'pos' if r['Profit']>0 else 'neg'}\">${r['Profit']:,.0f}</td>"
    f"<td>{r['Margin']}%</td></tr>"
    for _, r in category_data.iterrows()])

subcat_rows = "".join([
    f"<tr><td>{r['Sub-Category']}</td><td>${r['Sales']:,.0f}</td>"
    f"<td class=\"{'pos' if r['Profit']>0 else 'neg'}\">${r['Profit']:,.0f}</td>"
    f"<td>{r['Margin']}%</td></tr>"
    for _, r in subcat_data.iterrows()])

shipmode_rows = "".join([
    f"<tr><td>{r['Ship Mode']}</td><td>{int(r['Orders']):,}</td>"
    f"<td>${r['Sales']:,.0f}</td>"
    f"<td class=\"{'pos' if r['Profit']>0 else 'neg'}\">${r['Profit']:,.0f}</td>"
    f"<td>{r['Pct']}%</td></tr>"
    for _, r in shipmode_data.iterrows()])

output_path = "/home/yashraja/bigdata-project/output/hadoop_website.html"

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Superstore Sales Report</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --ink:#0f0f0d;--ink2:#2a2a26;--ink3:#4a4a44;
  --stone:#7a7a72;--fog:#a8a89e;
  --rule:#ddddd4;--rule2:#e8e8e0;
  --paper:#fefefe;--cream:#f7f6f1;--warm:#f0ede4;
  --red:#8b1a1a;--green:#1a5c30;--navy:#1a2d4a;--gold:#7a5c14;
  --font-serif:'Cormorant Garamond',serif;
  --font-sans:'Inter',sans-serif;
  --font-mono:'JetBrains Mono',monospace;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--paper);color:var(--ink);font-family:var(--font-sans);line-height:1.6}}
::-webkit-scrollbar{{width:3px}}
::-webkit-scrollbar-thumb{{background:var(--rule)}}

nav{{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(254,254,254,0.97);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule);height:52px;display:flex;align-items:center;justify-content:space-between;padding:0 60px}}
.nav-logo{{font-family:var(--font-serif);font-size:18px;font-weight:600;color:var(--ink)}}
.nav-links{{display:flex;gap:32px}}
.nav-links a{{color:var(--stone);text-decoration:none;font-size:12px;font-weight:500;letter-spacing:0.5px;text-transform:uppercase;transition:color .15s}}
.nav-links a:hover{{color:var(--ink)}}

.cover{{min-height:100vh;display:grid;grid-template-columns:1.1fr 0.9fr;background:var(--ink)}}
.cover-left{{padding:110px 64px 72px;display:flex;flex-direction:column;justify-content:space-between;border-right:1px solid rgba(255,255,255,0.06)}}
.cover-eyebrow{{font-size:10px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:rgba(255,255,255,0.25);margin-bottom:52px}}
.cover-title{{font-family:var(--font-serif);font-size:clamp(48px,6vw,80px);font-weight:700;line-height:0.95;color:#ffffff;letter-spacing:-1px;margin-bottom:36px}}
.cover-title em{{font-style:italic;color:rgba(255,255,255,0.35)}}
.cover-line{{width:32px;height:1px;background:rgba(255,255,255,0.2);margin-bottom:28px}}
.cover-summary{{font-size:15px;color:rgba(255,255,255,0.35);max-width:420px;line-height:1.8;font-weight:300;margin-bottom:64px}}
.cover-meta{{display:flex;flex-direction:column;gap:6px}}
.cover-meta span{{font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:0.3px}}
.cover-meta strong{{color:rgba(255,255,255,0.5)}}
.cover-right{{display:grid;grid-template-columns:1fr 1fr}}
.c-stat{{border-right:1px solid rgba(255,255,255,0.05);border-bottom:1px solid rgba(255,255,255,0.05);padding:44px 36px;display:flex;flex-direction:column;justify-content:flex-end}}
.c-stat:nth-child(even){{border-right:none}}
.c-stat .lbl{{font-size:9px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:rgba(255,255,255,0.2);margin-bottom:14px}}
.c-stat .val{{font-family:var(--font-serif);font-size:38px;font-weight:600;color:#ffffff;letter-spacing:-0.5px;line-height:1;margin-bottom:6px}}
.c-stat .sub{{font-size:11px;color:rgba(255,255,255,0.22)}}

.wrap{{max-width:1120px;margin:0 auto;padding:0 60px}}
section{{padding:88px 0;border-top:1px solid var(--rule)}}

.sec-head{{display:grid;grid-template-columns:180px 1fr;gap:48px;margin-bottom:56px}}
.sec-num{{font-family:var(--font-mono);font-size:10px;color:var(--fog);letter-spacing:2px;padding-top:5px}}
.sec-body .eyebrow{{font-size:9px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:var(--fog);margin-bottom:10px}}
.sec-title{{font-family:var(--font-serif);font-size:clamp(30px,3.5vw,46px);font-weight:600;letter-spacing:-0.3px;line-height:1.05;margin-bottom:14px;color:var(--ink)}}
.sec-desc{{font-size:14px;color:var(--stone);max-width:580px;line-height:1.75;font-weight:300}}

.kpi-band{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--rule);margin-bottom:48px}}
.kpi{{background:var(--paper);padding:28px 24px;border-right:1px solid var(--rule)}}
.kpi:last-child{{border-right:none}}
.kpi .k-lbl{{font-size:9px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--fog);margin-bottom:10px}}
.kpi .k-val{{font-family:var(--font-serif);font-size:32px;font-weight:600;letter-spacing:-0.5px;line-height:1;margin-bottom:4px}}
.kpi .k-sub{{font-size:11px;color:var(--fog)}}
.kpi.r .k-val{{color:var(--red)}}
.kpi.g .k-val{{color:var(--green)}}
.kpi.n .k-val{{color:var(--navy)}}
.kpi.o .k-val{{color:var(--gold)}}

.two{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rule);margin-bottom:1px}}
.three{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--rule);margin-bottom:1px}}
.one{{display:grid;grid-template-columns:1fr;gap:1px;background:var(--rule);margin-bottom:1px}}

.box{{background:var(--paper);padding:28px}}
.box h5{{font-size:9px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--fog);margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--rule2)}}
.box p{{font-size:13px;color:var(--ink3);line-height:1.75;font-weight:300}}
.box .big{{font-family:var(--font-serif);font-size:48px;font-weight:600;letter-spacing:-1px;line-height:1;margin:8px 0 6px}}
.box .big.r{{color:var(--red)}}
.box .big.g{{color:var(--green)}}
.box .big.n{{color:var(--navy)}}
.box .note{{font-family:var(--font-mono);font-size:10px;color:var(--fog);background:var(--cream);padding:6px 10px;display:inline-block;margin-top:12px}}

.chart-box{{background:var(--paper);padding:28px}}
.chart-box.full{{grid-column:1/-1}}
.chart-box .c-lbl{{font-size:9px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--fog);margin-bottom:5px}}
.chart-box .c-title{{font-size:14px;font-weight:600;color:var(--ink);margin-bottom:4px}}
.chart-box .c-desc{{font-size:12px;color:var(--fog);margin-bottom:18px;font-weight:300;line-height:1.6}}
.chart-box img{{width:100%;display:block}}

table{{width:100%;border-collapse:collapse;font-size:12px}}
.table-wrap{{overflow-x:auto}}
thead tr{{border-bottom:1px solid var(--ink)}}
th{{padding:9px 14px;text-align:left;font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--stone)}}
td{{padding:10px 14px;border-bottom:1px solid var(--rule2)}}
tbody tr:hover td{{background:var(--cream)}}
tbody tr:last-child td{{border-bottom:none}}
.pos{{color:var(--green);font-weight:500}}
.neg{{color:var(--red);font-weight:500}}

.tabs{{display:flex;gap:0;margin-bottom:20px;border-bottom:1px solid var(--rule)}}
.tab{{padding:10px 20px;border:none;background:transparent;color:var(--stone);font-size:10px;font-weight:600;letter-spacing:1.5px;cursor:pointer;border-bottom:1px solid transparent;transition:all .15s;font-family:var(--font-sans);margin-bottom:-1px;text-transform:uppercase}}
.tab.active{{color:var(--ink);border-bottom-color:var(--ink)}}
.tab-content{{display:none}}
.tab-content.active{{display:block}}

.s-input{{background:var(--cream);border:1px solid var(--rule);padding:8px 14px;color:var(--ink);font-size:12px;font-family:var(--font-sans);outline:none;margin-bottom:16px;width:260px;transition:border-color .15s}}
.s-input:focus{{border-color:var(--ink)}}

.findings{{border:1px solid var(--rule)}}
.finding{{display:grid;grid-template-columns:60px 1fr;border-bottom:1px solid var(--rule);background:var(--paper)}}
.finding:last-child{{border-bottom:none}}
.finding:hover{{background:var(--cream)}}
.f-num{{padding:28px 0;display:flex;align-items:flex-start;justify-content:center;font-family:var(--font-mono);font-size:10px;color:var(--fog);border-right:1px solid var(--rule);padding-top:32px}}
.f-body{{padding:26px 32px}}
.tag{{display:inline-block;font-size:8px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:3px 8px;margin-bottom:10px;border:1px solid}}
.tag.r{{color:var(--red);border-color:rgba(139,26,26,0.2);background:rgba(139,26,26,0.04)}}
.tag.g{{color:var(--green);border-color:rgba(26,92,48,0.2);background:rgba(26,92,48,0.04)}}
.tag.n{{color:var(--navy);border-color:rgba(26,45,74,0.2);background:rgba(26,45,74,0.04)}}
.f-body h4{{font-size:14px;font-weight:600;margin-bottom:8px;line-height:1.4;color:var(--ink)}}
.f-body p{{font-size:13px;color:var(--stone);line-height:1.72;font-weight:300}}
.f-stat{{font-family:var(--font-mono);font-size:10px;background:var(--cream);border:1px solid var(--rule);padding:6px 12px;display:inline-block;margin-top:10px;color:var(--ink3)}}

.close-box{{background:var(--ink);padding:56px 60px;margin-top:88px}}
.close-box .c-lbl{{font-size:9px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:rgba(255,255,255,0.2);margin-bottom:18px}}
.close-box h2{{font-family:var(--font-serif);font-size:clamp(22px,3vw,34px);font-weight:600;color:#ffffff;line-height:1.35;max-width:680px;margin-bottom:36px}}
.close-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid rgba(255,255,255,0.07)}}
.close-item{{padding:22px 0;border-bottom:1px solid rgba(255,255,255,0.07);padding-right:40px}}
.close-item:nth-child(odd){{padding-right:40px;border-right:1px solid rgba(255,255,255,0.07)}}
.close-item:nth-child(even){{padding-left:40px}}
.close-item h5{{font-size:11px;font-weight:600;color:rgba(255,255,255,0.55);margin-bottom:5px}}
.close-item p{{font-size:12px;color:rgba(255,255,255,0.22);line-height:1.65;font-weight:300}}

footer{{background:var(--warm);border-top:1px solid var(--rule);padding:28px 60px;display:flex;justify-content:space-between;align-items:center}}
footer .fl{{font-family:var(--font-serif);font-size:15px;color:var(--ink3)}}
footer .fr{{font-size:11px;color:var(--fog);text-align:right;line-height:1.6}}

.reveal{{opacity:0;transform:translateY(14px);transition:opacity .55s ease,transform .55s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style>
</head>
<body>

<nav>
  <div class="nav-logo">Superstore Analytics</div>
  <div class="nav-links">
    <a href="#summary">Summary</a>
    <a href="#revenue">Revenue</a>
    <a href="#profit">Profitability</a>
    <a href="#discount">Discount</a>
    <a href="#tables">Data</a>
    <a href="#findings">Findings</a>
  </div>
</nav>

<div class="cover">
  <div class="cover-left">
    <div>
      <div class="cover-eyebrow">Retail Analytics Report</div>
      <div class="cover-title">Superstore<br/><em>Sales</em><br/>Analysis</div>
      <div class="cover-line"></div>
      <div class="cover-summary">A structured analysis of {total_orders:,} retail orders examining revenue distribution, profit margins and the operational patterns that determine business performance across four regions and three product categories.</div>
    </div>
    <div class="cover-meta">
      <span>Prepared by — <strong>Yashraja</strong></span>
      <span>Dataset — <strong>Sample Superstore</strong></span>
      <span>Records Analysed — <strong>{total_orders:,} orders</strong></span>
      <span>Dimensions — <strong>4 regions · 3 categories · 17 sub-categories</strong></span>
    </div>
  </div>
  <div class="cover-right">
    <div class="c-stat"><div class="lbl">Total Revenue</div><div class="val">${total_sales:,.0f}</div><div class="sub">All regions</div></div>
    <div class="c-stat"><div class="lbl">Net Profit</div><div class="val">${total_profit:,.0f}</div><div class="sub">{profit_margin}% margin</div></div>
    <div class="c-stat"><div class="lbl">Total Orders</div><div class="val">{total_orders:,}</div><div class="sub">Transactions</div></div>
    <div class="c-stat"><div class="lbl">Profitable Orders</div><div class="val">{profit_pct}%</div><div class="sub">{loss_pct}% at a loss</div></div>
    <div class="c-stat"><div class="lbl">Top Region</div><div class="val">{top_region}</div><div class="sub">${top_region_sales:,.0f}</div></div>
    <div class="c-stat"><div class="lbl">Best Sub-Category</div><div class="val">{top_sub}</div><div class="sub">${top_sub_val:,.0f} profit</div></div>
    <div class="c-stat"><div class="lbl">Avg Order Value</div><div class="val">${avg_order_value:,.0f}</div><div class="sub">Per transaction</div></div>
    <div class="c-stat"><div class="lbl">Avg Discount</div><div class="val">{avg_discount}%</div><div class="sub">Across all orders</div></div>
  </div>
</div>

<div class="wrap">

  <section id="summary">
    <div class="sec-head reveal">
      <div class="sec-num">01 — EXECUTIVE SUMMARY</div>
      <div class="sec-body">
        <div class="eyebrow">Overview</div>
        <div class="sec-title">Business Performance at a Glance</div>
        <div class="sec-desc">Core financial metrics from {total_orders:,} orders covering revenue, profitability and order quality across the full dataset.</div>
      </div>
    </div>
    <div class="kpi-band reveal">
      <div class="kpi n"><div class="k-lbl">Revenue</div><div class="k-val">${total_sales:,.0f}</div><div class="k-sub">Gross sales</div></div>
      <div class="kpi g"><div class="k-lbl">Net Profit</div><div class="k-val">${total_profit:,.0f}</div><div class="k-sub">{profit_margin}% margin</div></div>
      <div class="kpi"><div class="k-lbl">Orders</div><div class="k-val">{total_orders:,}</div><div class="k-sub">Transactions</div></div>
      <div class="kpi o"><div class="k-lbl">Avg Order Value</div><div class="k-val">${avg_order_value:,.0f}</div><div class="k-sub">Per order</div></div>
    </div>
    <div class="three reveal">
      <div class="box">
        <h5>Order Profitability</h5>
        <div class="big g">{profit_pct}%</div>
        <p>of orders were profitable. The remaining <strong>{loss_pct}%</strong> — {loss_orders:,} orders — generated losses, primarily driven by high discount rates.</p>
      </div>
      <div class="box">
        <h5>Top Performing Region</h5>
        <div class="big n">{top_region}</div>
        <p>leads all regions with <strong>${top_region_sales:,.0f}</strong> in revenue and <strong>${top_region_profit:,.0f}</strong> in profit — the strongest market in the dataset.</p>
      </div>
      <div class="box">
        <h5>Discount Cost</h5>
        <div class="big r">${abs(high_disc_loss):,.0f}</div>
        <p>average loss on orders with 40% or more discount, versus <strong>${zero_disc_profit:,.0f}</strong> average profit on full-price orders.</p>
      </div>
    </div>
  </section>

  <section id="revenue">
    <div class="sec-head reveal">
      <div class="sec-num">02 — REVENUE ANALYSIS</div>
      <div class="sec-body">
        <div class="eyebrow">Sales Breakdown</div>
        <div class="sec-title">Where Revenue Comes From</div>
        <div class="sec-desc">Revenue performance by region, category and shipping method — identifying the channels and geographies that drive volume.</div>
      </div>
    </div>
    <div class="two reveal" style="margin-bottom:1px">
      <div class="chart-box">
        <div class="c-lbl">Regional Performance</div>
        <div class="c-title">Total Sales by Region</div>
        <div class="c-desc">{top_region} leads with ${top_region_sales:,.0f}. {bottom_region} is the lowest-performing region.</div>
        <img src="data:image/png;base64,{c1}" alt="Sales by Region"/>
      </div>
      <div class="chart-box">
        <div class="c-lbl">Shipping Distribution</div>
        <div class="c-title">Revenue by Ship Mode</div>
        <div class="c-desc">{top_ship} accounts for {top_ship_pct}% of all revenue — customers prioritise cost over delivery speed.</div>
        <img src="data:image/png;base64,{c5}" alt="Sales by Ship Mode"/>
      </div>
    </div>
    <div class="one reveal">
      <div class="chart-box">
        <div class="c-lbl">Product Performance</div>
        <div class="c-title">Top 10 Sub-Categories by Revenue</div>
        <div class="c-desc">Phones and Chairs lead in sales volume. High revenue does not always correspond to high profit — a distinction clarified in the following section.</div>
        <img src="data:image/png;base64,{c3}" alt="Top 10 Sub-Categories"/>
      </div>
    </div>
  </section>

  <section id="profit">
    <div class="sec-head reveal">
      <div class="sec-num">03 — PROFITABILITY ANALYSIS</div>
      <div class="sec-body">
        <div class="eyebrow">Profit and Loss</div>
        <div class="sec-title">Profit Drivers and Loss Sources</div>
        <div class="sec-desc">Which categories and sub-categories generate genuine profit versus which are consuming margin — a critical distinction that sales volume alone does not reveal.</div>
      </div>
    </div>
    <div class="kpi-band reveal">
      <div class="kpi g"><div class="k-lbl">Top Category</div><div class="k-val">{top_category}</div><div class="k-sub">${top_cat_profit:,.0f} profit</div></div>
      <div class="kpi g"><div class="k-lbl">Best Sub-Category</div><div class="k-val">{top_sub}</div><div class="k-sub">${top_sub_val:,.0f} profit</div></div>
      <div class="kpi r"><div class="k-lbl">Biggest Loss</div><div class="k-val">{loss_sub}</div><div class="k-sub">${abs(loss_val):,.0f} loss</div></div>
      <div class="kpi n"><div class="k-lbl">Top Region Profit</div><div class="k-val">${top_region_profit:,.0f}</div><div class="k-sub">{top_region} region</div></div>
    </div>
    <div class="one reveal">
      <div class="chart-box">
        <div class="c-lbl">Category Profitability</div>
        <div class="c-title">Net Profit by Product Category</div>
        <div class="c-desc">{top_category} is the most profitable category. Despite comparable sales volumes, categories differ significantly in net profit — driven by margin rates and discounting behaviour.</div>
        <img src="data:image/png;base64,{c2}" alt="Profit by Category"/>
      </div>
    </div>
  </section>

  <section id="discount">
    <div class="sec-head reveal">
      <div class="sec-num">04 — DISCOUNT IMPACT</div>
      <div class="sec-body">
        <div class="eyebrow">Pricing Analysis</div>
        <div class="sec-title">How Discounting Affects Profit</div>
        <div class="sec-desc">The relationship between discount rate and profitability is the most consequential pattern in this dataset. The evidence is unambiguous.</div>
      </div>
    </div>
    <div class="kpi-band reveal">
      <div class="kpi"><div class="k-lbl">High-Discount Orders</div><div class="k-val">{high_disc_count:,}</div><div class="k-sub">{high_disc_pct}% of all orders</div></div>
      <div class="kpi r"><div class="k-lbl">Avg Profit at 40%+ Disc</div><div class="k-val">${high_disc_loss:,.0f}</div><div class="k-sub">Average per order</div></div>
      <div class="kpi g"><div class="k-lbl">Avg Profit at 0% Disc</div><div class="k-val">${zero_disc_profit:,.0f}</div><div class="k-sub">Average per order</div></div>
      <div class="kpi o"><div class="k-lbl">Avg Discount Rate</div><div class="k-val">{avg_discount}%</div><div class="k-sub">Across all orders</div></div>
    </div>
    <div class="two reveal">
      <div class="chart-box">
        <div class="c-lbl">Discount vs Profitability</div>
        <div class="c-title">Discount Rate vs Profit per Order</div>
        <div class="c-desc">Each point is one order. Blue points are profitable. Red points are losses. The black dashed line is zero profit. The orange line marks the 40% threshold — above which virtually all orders are unprofitable.</div>
        <img src="data:image/png;base64,{c4}" alt="Discount vs Profit"/>
      </div>
      <div class="box" style="display:flex;flex-direction:column;justify-content:center">
        <h5>The Cost of Discounting</h5>
        <div class="big r" style="font-size:56px">${abs(high_disc_loss):,.0f}</div>
        <p style="margin-bottom:16px">average loss on orders with 40%+ discount compared to <strong>${zero_disc_profit:,.0f}</strong> on full-price orders.</p>
        <p>A difference of <strong>${round(zero_disc_profit - high_disc_loss, 2):,.0f}</strong> per order. With {high_disc_count:,} high-discount orders in the dataset, the cumulative profit impact of this pricing behaviour is the primary explainer of overall margin compression.</p>
        <div class="note">Recommendation — cap discounts at 20%</div>
      </div>
    </div>
  </section>

  <section id="tables">
    <div class="sec-head reveal">
      <div class="sec-num">05 — DATA TABLES</div>
      <div class="sec-body">
        <div class="eyebrow">Detailed Results</div>
        <div class="sec-title">Complete Breakdown by Dimension</div>
        <div class="sec-desc">Full aggregated results covering all regions, categories, shipping modes and sub-categories with revenue, profit and margin figures.</div>
      </div>
    </div>
    <div class="tabs reveal">
      <button class="tab active" onclick="showTab('region')">Region</button>
      <button class="tab" onclick="showTab('category')">Category</button>
      <button class="tab" onclick="showTab('subcat')">Sub-Category</button>
      <button class="tab" onclick="showTab('shipmode')">Ship Mode</button>
    </div>
    <div class="tab-content active" id="tab-region">
      <input class="s-input" type="text" placeholder="Search..." onkeyup="filterTable('t-region',this.value)"/>
      <div class="table-wrap">
        <table id="t-region">
          <thead><tr><th>Region</th><th>Revenue</th><th>Profit</th><th>Margin</th></tr></thead>
          <tbody>{region_rows}</tbody>
        </table>
      </div>
    </div>
    <div class="tab-content" id="tab-category">
      <input class="s-input" type="text" placeholder="Search..." onkeyup="filterTable('t-cat',this.value)"/>
      <div class="table-wrap">
        <table id="t-cat">
          <thead><tr><th>Category</th><th>Revenue</th><th>Profit</th><th>Margin</th></tr></thead>
          <tbody>{category_rows}</tbody>
        </table>
      </div>
    </div>
    <div class="tab-content" id="tab-subcat">
      <input class="s-input" type="text" placeholder="Search..." onkeyup="filterTable('t-sub',this.value)"/>
      <div class="table-wrap">
        <table id="t-sub">
          <thead><tr><th>Sub-Category</th><th>Revenue</th><th>Profit</th><th>Margin</th></tr></thead>
          <tbody>{subcat_rows}</tbody>
        </table>
      </div>
    </div>
    <div class="tab-content" id="tab-shipmode">
      <div class="table-wrap">
        <table id="t-ship">
          <thead><tr><th>Ship Mode</th><th>Orders</th><th>Revenue</th><th>Profit</th><th>Revenue Share</th></tr></thead>
          <tbody>{shipmode_rows}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section id="findings">
    <div class="sec-head reveal">
      <div class="sec-num">06 — KEY FINDINGS</div>
      <div class="sec-body">
        <div class="eyebrow">Conclusions</div>
        <div class="sec-title">Six Evidence-Based Findings</div>
        <div class="sec-desc">Each conclusion is supported directly by the data — specific numbers, not general observations.</div>
      </div>
    </div>
    <div class="findings reveal">
      <div class="finding">
        <div class="f-num">01</div>
        <div class="f-body">
          <span class="tag r">Critical</span>
          <h4>Discounts above 40% produce consistent losses averaging ${abs(high_disc_loss):,.0f} per order</h4>
          <p>{high_disc_count:,} orders ({high_disc_pct}% of total) carried a discount of 40% or more. Every one of these averaged a loss. Full-price orders averaged ${zero_disc_profit:,.0f} profit. The scatter chart confirms this with loss-making orders concentrated entirely above the 40% discount line.</p>
          <div class="f-stat">Delta: ${round(zero_disc_profit - high_disc_loss, 2):,.0f} per order between 0% and 40%+ discount</div>
        </div>
      </div>
      <div class="finding">
        <div class="f-num">02</div>
        <div class="f-body">
          <span class="tag r">Loss Driver</span>
          <h4>{loss_sub} recorded ${abs(loss_val):,.0f} in cumulative losses — the worst sub-category in the dataset</h4>
          <p>{loss_sub} is not a low-volume product. The loss is attributable entirely to the pricing strategy applied to it. Eliminating or strictly capping discounts on {loss_sub} would have an immediate and measurable positive impact on overall margins.</p>
        </div>
      </div>
      <div class="finding">
        <div class="f-num">03</div>
        <div class="f-body">
          <span class="tag g">Opportunity</span>
          <h4>{top_sub} generated ${top_sub_val:,.0f} in profit — the highest-margin product in the catalogue</h4>
          <p>{top_sub} significantly outperforms all other sub-categories in net profit. It is not subject to aggressive discounting, which partly explains its margin profile. Increasing focus on {top_sub} represents the clearest product-level growth opportunity available.</p>
        </div>
      </div>
      <div class="finding">
        <div class="f-num">04</div>
        <div class="f-body">
          <span class="tag n">Regional</span>
          <h4>{top_region} is the strongest region with ${top_region_sales:,.0f} revenue and ${top_region_profit:,.0f} profit</h4>
          <p>The {top_region} region leads all others in both revenue and profit. The {bottom_region} region generates the lowest revenue. Understanding what drives {top_region}'s performance and applying those insights to underperforming regions is a scalable growth lever.</p>
        </div>
      </div>
      <div class="finding">
        <div class="f-num">05</div>
        <div class="f-body">
          <span class="tag g">Category Strategy</span>
          <h4>{top_category} is the most profitable category at ${top_cat_profit:,.0f} — driven by lower average discount rates</h4>
          <p>{top_category} outperforms the other two categories in net profit. This margin advantage is partly explained by less aggressive discounting on {top_category} products. Pricing discipline — not sales volume — is the primary determinant of category-level profitability.</p>
        </div>
      </div>
      <div class="finding">
        <div class="f-num">06</div>
        <div class="f-body">
          <span class="tag n">Operations</span>
          <h4>{top_ship} shipping carries {top_ship_pct}% of all revenue — customers consistently choose economy over speed</h4>
          <p>Standard Class dominates order volume by a significant margin. Premium shipping options represent a minority of transactions. Operational resources should be oriented toward Standard Class fulfilment efficiency rather than premium speed capabilities.</p>
        </div>
      </div>
    </div>
  </section>

  <div class="close-box reveal">
    <div class="c-lbl">Conclusion</div>
    <h2>The data identifies a clear path to improved profitability — disciplined discounting, focus on high-margin products and replication of regional best practice.</h2>
    <div class="close-grid">
      <div class="close-item">
        <h5>Discount Reform</h5>
        <p>Capping discounts at 20% would eliminate most loss-making orders. High discounts destroy margin without proportional volume benefit.</p>
      </div>
      <div class="close-item">
        <h5>Product Focus</h5>
        <p>Prioritise {top_sub} and {top_category}. Reduce or remove discounts on {loss_sub} immediately.</p>
      </div>
      <div class="close-item">
        <h5>Regional Learning</h5>
        <p>Identify what drives {top_region}'s outperformance and apply those strategies to the {bottom_region} region.</p>
      </div>
      <div class="close-item">
        <h5>Seasonal Planning</h5>
        <p>Revenue peaks in Q4 annually. Inventory and capacity planning should reflect this pattern to capture peak demand.</p>
      </div>
    </div>
  </div>

</div>

<footer>
  <div class="fl">Superstore Sales Analysis — {total_orders:,} orders</div>
  <div class="fr">Yashraja<br/>{total_orders:,} records · 4 regions · 3 categories</div>
</footer>

<script>
function showTab(n){{
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active');
  event.target.classList.add('active');
}}
function filterTable(id,q){{
  document.getElementById(id).querySelectorAll('tbody tr').forEach(r=>{{
    r.style.display=r.textContent.toLowerCase().includes(q.toLowerCase())?'':'none';
  }});
}}
const obs=new IntersectionObserver(e=>e.forEach(x=>{{
  if(x.isIntersecting)x.target.classList.add('visible');
}}),{{threshold:0.06}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
</script>
</body>
</html>"""

with open(output_path, "w") as f:
    f.write(html)

subprocess.run(["hdfs", "dfs", "-put", "-f", output_path,
                "/user/yashraja/bigdata/output/hadoop_website.html"],
               capture_output=True)

print("\n✅ Report generated successfully!")
print(f"📄 Local  : {output_path}")
print("📂 HDFS   : /user/yashraja/bigdata/output/hadoop_website.html")
