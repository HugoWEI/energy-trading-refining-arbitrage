"""Interactive research dashboard: streamlit run dashboard.py"""
import plotly.express as px
import streamlit as st
from energy_trading.data import DEFAULT_PATH, load_weekly_prices, SNAPSHOT_SOURCE
from energy_trading.pricing import add_crack_metrics, crack_decomposition
from energy_trading.arbitrage import (
    CargoAssumptions, indicative_margin_usd_bbl, breakeven_brent_usd_bbl, scenario_grid
)

st.set_page_config(page_title="Energy Trading | Refining & Arbitrage", layout="wide")
st.title("Energy Trading: Refining Margins & Physical Arbitrage")
st.warning(
    "Research prototype, NOT a trading signal. Historical EIA weekly-average spot prices; "
    "crude grades and price locations differ. Cargo costs are hypothetical. Not real-time quotes."
)
path = st.sidebar.text_input("Weekly EIA CSV path", str(DEFAULT_PATH))
try:
    df = add_crack_metrics(load_weekly_prices(path))
except (OSError, ValueError) as exc:
    st.error(f"Cannot load data: {exc}")
    st.stop()
last = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else None
st.caption(
    f"Observations: {df['week_ending'].min():%d %b %Y} to "
    f"{df['week_ending'].max():%d %b %Y} | [EIA primary source]({SNAPSHOT_SOURCE})"
)
a, b, c, d = st.columns(4)
a.metric("WTI Cushing USD/bbl", f"{last['wti_cushing_usd_bbl']:.2f}")
b.metric("Brent Europe USD/bbl", f"{last['brent_europe_usd_bbl']:.2f}")
c.metric("Gross 3-2-1 crack USD/bbl", f"{last['crack_321_usd_bbl']:.2f}")
d.metric("Brent-WTI benchmark USD/bbl", f"{last['brent_wti_spread_usd_bbl']:.2f}")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Refining economics", "Cargo scenario analysis", "Source data", "Trader interview"]
)
with tab1:
    st.latex(r"Crack_{3:2:1}=\frac{2\cdot 42G+42D-3W}{3}")
    st.plotly_chart(px.line(
        df, x="week_ending", y="crack_321_usd_bbl", markers=True,
        title="EIA weekly spot-price 3-2-1 gross crack proxy"
    ), use_container_width=True)
    if previous is not None:
        change = crack_decomposition(previous, last)
        st.plotly_chart(px.bar(
            x=list(change), y=list(change.values()),
            title="Exact arithmetic attribution of weekly crack change"
        ), use_container_width=True)
        st.caption("This is an arithmetic attribution, not proof of fundamental causation.")
    st.info(
        "3-2-1 is a theoretical gross spread, not refinery profit. "
        "Refinery yield, energy, blending, grade, geography and operating costs matter."
    )
with tab2:
    st.markdown("#### Hypothetical US-to-Europe crude export screening")
    st.caption("Benchmark proxies plus user-editable EXAMPLE costs, not executable cargo quotes.")
    x, y, z = st.columns(3)
    with x:
        inland = st.slider("Inland logistics USD/bbl", 0., 12., 3.5, 0.25)
        marine = st.slider("Ocean freight USD/bbl", 0., 15., 3.75, 0.25)
    with y:
        terminal = st.slider("Terminal USD/bbl", 0., 8., 1.5, 0.25)
        insurance = st.slider("Insurance USD/bbl", 0., 5., 0.45, 0.05)
    with z:
        financing = st.slider("Financing USD/bbl", 0., 6., 0.35, 0.05)
        grade = st.slider("Grade/basis adjustment USD/bbl", -10., 20., 4., 0.5)
    loss = st.slider("Volume loss %", 0., 3., .5, .1)
    assumptions = CargoAssumptions(inland, marine, terminal, insurance, financing, grade, loss)
    margin = indicative_margin_usd_bbl(
        last["wti_cushing_usd_bbl"], last["brent_europe_usd_bbl"], assumptions
    )
    st.metric("Illustrative screening differential (USD/input bbl)", f"{margin:+.2f}")
    st.caption("Break-even Brent proxy (USD/bbl): {:.2f}".format(
        breakeven_brent_usd_bbl(last["wti_cushing_usd_bbl"], assumptions)
    ))
    scenarios = scenario_grid(
        last["wti_cushing_usd_bbl"], last["brent_europe_usd_bbl"], assumptions
    ).pivot(
        index="Freight shock ($/bbl)", columns="Brent shock ($/bbl)",
        values="Illustrative margin ($/bbl)"
    )
    st.plotly_chart(px.imshow(
        scenarios, text_auto=".1f", color_continuous_scale="RdBu",
        title="Freight and benchmark spread sensitivity (not executable P&L)"
    ), use_container_width=True)
    st.error(
        "Do not trade this differential: grade, location, laycan and freight basis do not match. "
        "A physical desk requires FOB US Gulf Coast export and CIF Europe cargo bids/offers "
        "plus actual freight, quality, insurance, storage, taxes and hedge basis."
    )
with tab3:
    st.dataframe(df, hide_index=True)
    st.download_button(
        "Download audited calculated data",
        df.to_csv(index=False, date_format="%Y-%m-%d").encode(),
        "weekly_analytics.csv", mime="text/csv"
    )
with tab4:
    st.markdown("#### Thirty-second trader interview explanation")
    st.write(
        f"In the EIA week ending {last['week_ending']:%d %B %Y}, "
        f"the gross US 3-2-1 crack proxy is USD {last['crack_321_usd_bbl']:.2f} per crude barrel. "
        "My project separates mechanical price contributions from fundamental causes, then "
        "stress-tests a deliberately hypothetical cargo differential against freight and grade. "
        "A wide Brent-WTI screen is not automatically tradeable: I would seek comparable "
        "FOB/CIF same-grade cargo assessments, matched delivery windows, inventories, "
        "vessel quotations and a plan to hedge location and timing basis."
    )
