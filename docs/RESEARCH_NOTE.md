# Research Note 01 — Crude and Product Margins

**16 October 2026 | Descriptive prototype, not investment advice or evidence of trading alpha.**

## Data and methodology
- Public [EIA weekly spot-price table](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_w.htm), released 15 October 2026.
- Six observations (4 September–9 October 2026), Friday-ending **weekly averages** of daily spot closing assessments.
- WTI **Cushing** and Brent **Europe** benchmarks: USD per barrel.
- Conventional regular gasoline and ULSD **US Gulf Coast**: USD per US gallon.

## Observations
For week ending **9 October 2026**: WTI 96.88 USD/bbl; Brent 127.43 USD/bbl; Gulf Coast gasoline 3.513 USD/gal; Gulf Coast ULSD 4.640 USD/gal. With the 42-gallon conversion, the indicative gross **3-2-1 crack proxy is 66.44 USD/crude bbl**. Brent Europe minus WTI Cushing equals 30.55 USD/bbl.

**Neither is an executable spread.** The first contains refinery yield/cost assumptions and incompatible location basis; the second compares different crude grades and price points. The shipping screen adds explicitly *illustrative*, not market-observed, inland/outbound freight, terminal, insurance, financing, volume loss and grade-basis adjustments.

## Trader-oriented reasoning
1. Observe: establish source, exact day/week, quote basis, quality and units.
2. Decompose: explain **which arithmetic inputs** changed the 3-2-1 crack; this is not yet a causal explanation.
3. Investigate: compare inventory draws, refinery runs, gasoline/diesel demand, OPEC, outages, freight and physical differentials using additional dated sources.
4. Evaluate: seek same-grade USGC FOB and Europe CIF bids/offers for *matching laycans*, vessel class and complete landed costs.
5. Stress: vary physical crude grade differentials, freight availability, interest costs, timing/basis and achievable hedges.

## What is still needed
Longer historical data, EIA inventories/refinery utilization, causal event studies, real cargo-market quotes and freight costs, forwarding curves, optionality/storage economics, and a petrochemical naphtha-vs-LPG feedstock case study. The six-week snapshot is **insufficient** for forecasting or backtesting.

**30-second explanation:** "I wanted to turn an observed commodity price spread into a testable economic question. I calculated a properly unit-converted crack and decomposed how gasoline, diesel and WTI mathematically affected it. For US–Europe crude flows I developed a cost-sensitivity screen, but I deliberately avoided calling Brent–WTI a tradable arb: crude quality, timing and FOB/CIF basis have to match first."
