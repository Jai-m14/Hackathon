"""Preview every VentureLens chart for one startup. Run: streamlit run charts_preview.py"""

import json
from pathlib import Path

import streamlit as st

import charts

DATA = Path(__file__).with_name("venturelens_comparable_data.json")

st.set_page_config(page_title="VentureLens charts preview", layout="wide")


@st.cache_data
def load_records() -> list[dict]:
    with DATA.open(encoding="utf-8") as f:
        return json.load(f)


records = load_records()
labels = {f"{r['Company_ID']} → {charts.chart_title(r)}": r for r in records}

with st.sidebar:
    choice = st.selectbox("Startup → Comparable (ticker)", list(labels))
    theme_choice = st.radio("Chart theme", ["Auto", "Light", "Dark"], horizontal=True)

record = labels[choice]
if theme_choice == "Auto":
    mode = getattr(st.context.theme, "type", None) or "light"
else:
    mode = theme_choice.lower()


def show(fig) -> None:
    # theme=None keeps the charts.py theme instead of Streamlit's default restyling.
    # width="stretch" is the current name for use_container_width=True.
    st.plotly_chart(fig, width="stretch", theme=None,
                    config={"displaylogo": False, "displayModeBar": False})


st.title(f"{record['Company_ID']} → {charts.chart_title(record)}")
match = record.get("llm_match") or {}
if match.get("rationale"):
    st.caption(f"Why this comparable ({match.get('confidence', '?')} confidence): {match['rationale']}")

show(charts.kpi_snapshot(record, mode=mode))

rows = [
    (charts.revenue_net_income(record, mode=mode), charts.margin_trends(record, mode=mode)),
    (charts.valuation_multiples(record, mode=mode), charts.returns_and_health(record, mode=mode)),
    (charts.earnings_surprises(record, mode=mode), charts.analyst_recommendations(record, mode=mode)),
    (charts.portfolio_comparables_scatter(records, record["Company_ID"], mode=mode),
     charts.news_volume(record, mode=mode)),
]
for left, right in rows:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        show(left)
    with c2:
        show(right)
