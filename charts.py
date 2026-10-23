"""VentureLens chart library: Plotly figures for a startup's matched public comparable.

Every function takes one record from ``venturelens_comparable_data.json`` (a dict) and
returns a ``plotly.graph_objects.Figure``. Missing or short data never raises: the
function returns a small "No data available for this chart" figure instead.

All functions also accept an optional ``mode="light" | "dark"`` keyword so colours match
the page theme. In Streamlit, render with ``st.plotly_chart(fig, theme=None, ...)`` so
Streamlit's own theme does not override ours. Figures set a height but no width, so
they fill the column they are placed in.

Usage::

    import json, charts
    records = json.load(open("venturelens_comparable_data.json", encoding="utf-8"))
    fig = charts.revenue_net_income(records[0], mode="dark")

Functions
---------
revenue_net_income(record) -> Figure
    Revenue and net income bars by fiscal year (auto-scaled to $M or $B), with a
    revenue YoY growth % line in a small panel underneath. Losses drawn in red.
margin_trends(record) -> Figure
    Gross, operating, net and FCF margin (%) over the last 10 years.
valuation_multiples(record) -> Figure
    P/S and EV/Revenue (left panel) and P/E (right panel), last 10 years. P/E values
    that are negative or above 200 are omitted, and the subtitle says which years.
returns_and_health(record) -> Figure
    ROE, ROIC, ROA (%) in one panel; current ratio and debt-to-equity (x) in another.
earnings_surprises(record) -> Figure
    Actual vs estimated EPS for the last 4 quarters; beats green, misses red.
analyst_recommendations(record) -> Figure
    Stacked analyst ratings per month, strong buy (green) to strong sell (red).
kpi_snapshot(record) -> Figure
    Tile grid: market cap, revenue growth, gross margin, net margin, P/S, beta and
    52-week price return (TTM).
portfolio_comparables_scatter(all_records, highlight_company_id) -> Figure
    One bubble per unique comparable: x = revenue growth TTM %, y = gross margin
    TTM %, size = market cap. The selected startup's comparable is highlighted.
news_volume(record) -> Figure
    Weekly count of news articles over the 90 days up to the data snapshot.

Helpers
-------
chart_title(record) -> str          e.g. "Arrow Electronics Inc (ARW)"
fmt_usd(v) -> str, fmt_pct(v) -> str  "$12.3B", "11.2%"; "—" when missing
"""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

__all__ = [
    "revenue_net_income",
    "margin_trends",
    "valuation_multiples",
    "returns_and_health",
    "earnings_surprises",
    "analyst_recommendations",
    "kpi_snapshot",
    "portfolio_comparables_scatter",
    "news_volume",
    "chart_title",
    "fmt_usd",
    "fmt_pct",
]

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
SOURCE_FIN = "Source: Finnhub, SEC filings"
SOURCE_MKT = "Source: Finnhub"

# Categorical slots are used in this fixed order; dark mode uses its own steps.
PALETTE = {
    "light": {
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"],
        "ink": "#0b0b0b",
        "ink2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "neutral": "#b5b3ab",
        "good": "#0ca30c",
        "good_strong": "#008300",
        "good_soft": "#7cc77c",
        "good_text": "#006300",
        "bad": "#d03b3b",
        "bad_soft": "#ec835a",
        "hover_bg": "#ffffff",
    },
    "dark": {
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500"],
        "ink": "#f0efec",
        "ink2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "neutral": "#5f5e5a",
        "good": "#0ca30c",
        "good_strong": "#0ca30c",
        "good_soft": "#4f8f4f",
        "good_text": "#0ca30c",
        "bad": "#d03b3b",
        "bad_soft": "#ec835a",
        "hover_bg": "#262624",
    },
}

HEIGHT = 420
HEIGHT_SMALL = 360


def _pal(mode: str) -> dict:
    return PALETTE["dark" if mode == "dark" else "light"]


def _style(fig: go.Figure, title: str, subtitle: str, source: str, mode: str,
           height: int = HEIGHT, legend: bool = True) -> go.Figure:
    """Apply the shared VentureLens look to a figure."""
    p = _pal(mode)
    sub = f"<br><span style='font-size:12px;color:{p['ink2']}'>{subtitle}</span>" if subtitle else ""
    fig.update_layout(
        height=height,
        autosize=True,
        font=dict(family=FONT, size=12, color=p["ink2"]),
        title=dict(text=f"{title}{sub}", x=0, xanchor="left", xref="paper", y=1,
                   yref="container", yanchor="top", pad=dict(t=14),
                   font=dict(size=16, color=p["ink"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=80 + 16 * subtitle.count("<br>"), b=56),
        showlegend=legend,
        legend=dict(orientation="h", x=0, xanchor="left", y=1.0, yanchor="bottom",
                    font=dict(size=11, color=p["ink2"]), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=p["hover_bg"], bordercolor=p["axis"],
                        font=dict(family=FONT, size=12, color=p["ink"])),
        bargap=0.3,
        bargroupgap=0.08,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=p["axis"], ticks="",
                     tickfont=dict(color=p["muted"]), automargin=True,
                     title_font=dict(size=11, color=p["muted"]))
    fig.update_yaxes(showgrid=True, gridcolor=p["grid"], gridwidth=1, zeroline=True,
                     zerolinecolor=p["axis"], zerolinewidth=1, showline=False, ticks="",
                     tickfont=dict(color=p["muted"]), automargin=True,
                     title_font=dict(size=11, color=p["muted"]))
    if source:
        fig.add_annotation(text=source, xref="paper", yref="paper", x=0, y=0,
                           yshift=-48, xanchor="left", yanchor="bottom", showarrow=False,
                           font=dict(size=10, color=p["muted"]), name="source")
    return fig


def _empty(title: str, mode: str, reason: str = "No data available for this chart",
           height: int = 220) -> go.Figure:
    fig = go.Figure()
    _style(fig, title, "", "", mode, height=height, legend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(text=reason, xref="paper", yref="paper", x=0.5, y=0.45,
                       showarrow=False, font=dict(size=13, color=_pal(mode)["muted"]))
    return fig


def _two_panel(left: str, right: str, widths=(0.5, 0.5)) -> go.Figure:
    return make_subplots(rows=1, cols=2, horizontal_spacing=0.12, column_widths=list(widths),
                         subplot_titles=(left, right))


def _finish_two_panel(fig: go.Figure, mode: str) -> None:
    """Style subplot titles and leave room for title + legend + panel titles."""
    p = _pal(mode)
    for a in fig.layout.annotations:
        if a.name != "source" and a.text and not a.text.startswith("Source"):
            a.update(font=dict(family=FONT, size=12, color=p["ink2"]))
    fig.update_layout(margin=dict(t=fig.layout.margin.t + 38), legend=dict(y=1.1))


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _num(x) -> float:
    """Coerce to float; anything missing or non-numeric becomes NaN (never 0)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return math.nan
    return v if math.isfinite(v) else math.nan


def _name(record: dict) -> str:
    """Short company name for titles: "Arrow Electronics Inc" -> "Arrow Electronics"."""
    record = record or {}
    name = record.get("display_name") or record.get("ticker") or "Comparable"
    for suffix in (" Inc", " Corp", " Ltd", " PLC"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def chart_title(record: dict) -> str:
    """Display label like "Arrow Electronics Inc (ARW)"."""
    record = record or {}
    t = record.get("ticker")
    n = record.get("display_name") or t or "Comparable"
    return f"{n} ({t})" if t and t != n else n


def _series(record: dict, metric: str, scale: float = 1.0) -> pd.Series:
    """Annual metric series indexed by year (int), oldest first, NaN for missing years."""
    rows = ((record or {}).get("metric_series_annual") or {}).get(metric) or []
    data = {}
    for r in rows:
        try:
            year = int(str(r.get("period", ""))[:4])
        except ValueError:
            continue
        data[year] = _num(r.get("v")) * scale
    if not data:
        return pd.Series(dtype=float)
    s = pd.Series(data).sort_index()
    return s.reindex(range(int(s.index.min()), int(s.index.max()) + 1))


def _frame(record: dict, metrics: dict, years: int = 10, scale: float = 1.0) -> pd.DataFrame:
    """Several metric series aligned on the same years, the last ``years`` years overall."""
    cols = {label: _series(record, key, scale) for label, key in metrics.items()}
    cols = {k: v for k, v in cols.items() if v.notna().any()}
    if not cols:
        return pd.DataFrame()
    df = pd.DataFrame(cols)
    df = df.reindex(range(int(df.index.min()), int(df.index.max()) + 1))
    last = int(df.dropna(how="all").index.max())
    df = df.loc[last - years + 1: last]
    return df.loc[df.dropna(how="all").index.min():]  # no empty leading years


def _scale_usd(values) -> tuple[float, str, str]:
    vals = [abs(v) for v in values if isinstance(v, (int, float)) and math.isfinite(v)]
    m = max(vals) if vals else 0
    if m >= 1e9:
        return 1e9, "B", "billions"
    if m >= 1e6:
        return 1e6, "M", "millions"
    return 1e3, "K", "thousands"


def fmt_usd(v, decimals: int = 1) -> str:
    """$12.3B / $450.0M / -$1.2B; em dash for missing."""
    v = _num(v)
    if math.isnan(v):
        return "—"
    sign = "-" if v < 0 else ""
    a = abs(v)
    for div, unit in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= div:
            return f"{sign}${a / div:,.{decimals}f}{unit}"
    return f"{sign}${a:,.0f}"


def fmt_pct(v, decimals: int = 1, signed: bool = False) -> str:
    """11.2% / +26.1%; em dash for missing. Input is already a percentage."""
    v = _num(v)
    if math.isnan(v):
        return "—"
    return f"{v:+,.{decimals}f}%" if signed else f"{v:,.{decimals}f}%"


def _add_lines(fig: go.Figure, df: pd.DataFrame, colors: list[str], fmt: str, suffix: str,
               row: int | None = None, col: int | None = None) -> None:
    """One 2px line per column; hover shows "<label> <year>: <value><suffix>".

    Also pins the x-axis to the year span so Plotly never autoranges it oddly.
    """
    kw = dict(row=row, col=col) if row else {}
    years = [int(y) for y in df.index]
    for i, label in enumerate(df.columns):
        c = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=years, y=df[label].tolist(), name=label, mode="lines+markers",
            line=dict(color=c, width=2), marker=dict(size=7, color=c),
            connectgaps=False,
            hovertemplate=f"<b>{label}</b> %{{x}}<br>%{{y:{fmt}}}{suffix}<extra></extra>",
        ), **kw)
    if years:
        fig.update_xaxes(range=[years[0] - 0.5, years[-1] + 0.5],
                         dtick=1 if len(years) <= 6 else 2, **kw)


PCT_FLOOR = -200  # values below this (e.g. one-off impairments) are drawn off-scale


def _clip_pct_axis(fig: go.Figure, df: pd.DataFrame, **kw) -> str:
    """Stop a % y-axis above extreme lows so the other years stay readable.

    Returns a subtitle note naming the off-scale values, or "" if nothing was clipped.
    """
    low = df[df < PCT_FLOOR].stack()
    if low.empty:
        return ""
    kept = df[df >= PCT_FLOOR]
    lo = min(float(kept.min().min()) if kept.notna().any().any() else 0.0, 0.0)
    hi = max(float(kept.max().max()) if kept.notna().any().any() else 0.0, 0.0)
    pad = (hi - lo) * 0.12 or 10
    fig.update_yaxes(range=[lo - pad, hi + pad], **kw)
    by_year: dict[int, list[str]] = {}
    for (year, label), v in low.items():
        by_year.setdefault(int(year), []).append(f"{label} {v:,.0f}%")
    items = "; ".join(f"{y}: {', '.join(v)}" for y, v in by_year.items())
    return f"<br>Off-scale, {items}."


# ---------------------------------------------------------------------------
# 1. Revenue and net income
# ---------------------------------------------------------------------------

def revenue_net_income(record: dict, mode: str = "light") -> go.Figure:
    """Revenue + net income bars by fiscal year, revenue YoY growth % panel below.

    Input: one comparable record. Output: Figure (height 420).
    """
    title = f"{_name(record)}: revenue and profit by year"
    data = {}
    for r in (record or {}).get("financials_annual") or []:
        try:
            fy = int(r.get("fiscal_year") or r.get("year"))
        except (TypeError, ValueError):
            continue
        data[fy] = (_num(r.get("revenue")), _num(r.get("net_income")))
    if not data:
        return _empty(title, mode)
    df = pd.DataFrame.from_dict(data, orient="index", columns=["revenue", "net_income"]).sort_index()
    df = df.reindex(range(int(df.index.min()), int(df.index.max()) + 1))
    if df[["revenue", "net_income"]].isna().all().all():
        return _empty(title, mode)
    prev = df["revenue"].shift(1)
    df["growth"] = (df["revenue"] / prev - 1) * 100
    df.loc[~(prev > 0), "growth"] = math.nan

    p = _pal(mode)
    div, unit, unit_word = _scale_usd(list(df["revenue"]) + list(df["net_income"]))
    years = [str(y) for y in df.index]
    has_growth = df["growth"].notna().any()

    fig = make_subplots(rows=2 if has_growth else 1, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28] if has_growth else [1.0],
                        vertical_spacing=0.1)
    fig.add_trace(go.Bar(
        x=years, y=df["revenue"] / div, name="Revenue", marker_color=p["series"][0],
        marker_line_width=0, customdata=[fmt_usd(v) for v in df["revenue"]],
        hovertemplate="<b>Revenue</b> FY%{x}<br>%{customdata}<extra></extra>",
    ), row=1, col=1)
    ni = df["net_income"]
    # Profit and loss are separate traces sharing one bar slot, so each gets its own
    # legend entry and colour.
    for name, part, color in (("Net income", ni.where(ni >= 0), p["series"][2]),
                              ("Net loss", ni.where(ni < 0), p["bad"])):
        if part.isna().all() and name == "Net loss":
            continue
        fig.add_trace(go.Bar(
            x=years, y=(part / div).tolist(), name=name, marker_color=color,
            marker_line_width=0, offsetgroup="net", customdata=[fmt_usd(v) for v in part],
            hovertemplate=f"<b>{name}</b> FY%{{x}}<br>%{{customdata}}<extra></extra>",
        ), row=1, col=1)
    fig.update_traces(offsetgroup="revenue", selector=dict(name="Revenue"))
    fig.update_yaxes(title_text=f"USD {unit_word}", tickprefix="$", ticksuffix=unit, row=1, col=1)
    if has_growth:
        g = df["growth"]
        fig.add_trace(go.Scatter(
            x=years, y=g, name="Revenue growth YoY", mode="lines+markers+text",
            line=dict(color=p["series"][1], width=2), marker=dict(size=7),
            text=["" if math.isnan(v) else fmt_pct(v, 0, signed=True) for v in g],
            textposition="top center", textfont=dict(size=10, color=p["ink2"]),
            cliponaxis=False, connectgaps=False,
            hovertemplate="<b>Revenue growth</b> FY%{x}<br>%{y:+.1f}% vs prior year<extra></extra>",
        ), row=2, col=1)
        lo, hi = min(0.0, g.min()), max(0.0, g.max())
        span = (hi - lo) or 10
        fig.update_yaxes(title_text="YoY", ticksuffix="%", nticks=3,
                         range=[lo - span * 0.15, hi + span * 0.45], row=2, col=1)
    fig.update_xaxes(type="category")
    note = "Fiscal years, USD. Lower panel: revenue growth vs prior year."
    missing = [str(y) for y in df.index[df["revenue"].isna()]]
    if missing:
        note += f" FY{', '.join(missing)} revenue not reported."
    _style(fig, title, note, SOURCE_FIN, mode, height=HEIGHT)
    fig.update_layout(barmode="group")
    return fig


# ---------------------------------------------------------------------------
# 2. Margins
# ---------------------------------------------------------------------------

MARGINS = {"Gross margin": "grossMargin", "Operating margin": "operatingMargin",
           "Net margin": "netMargin", "FCF margin": "fcfMargin"}


def margin_trends(record: dict, mode: str = "light") -> go.Figure:
    """Gross / operating / net / FCF margin (%), last 10 years.

    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: profit margins over time"
    df = _frame(record, MARGINS, years=10, scale=100)  # series are fractions -> %
    if df.empty or df.notna().sum().max() < 2:
        return _empty(title, mode)
    fig = go.Figure()
    _add_lines(fig, df, _pal(mode)["series"], ".1f", "%")
    fig.update_yaxes(ticksuffix="%")
    note = "Annual margins as % of revenue. Gaps = year not reported."
    note += _clip_pct_axis(fig, df)
    _style(fig, title, note, SOURCE_FIN, mode)
    return fig


# ---------------------------------------------------------------------------
# 3. Valuation multiples
# ---------------------------------------------------------------------------

PE_MAX = 200


def valuation_multiples(record: dict, mode: str = "light") -> go.Figure:
    """P/S and EV/Revenue (left) and P/E (right), last 10 years.

    P/E below 0 (losses) or above 200 is omitted; the subtitle names those years.
    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: valuation multiples"
    df = _frame(record, {"P/S": "ps", "EV/Revenue": "evRevenue", "P/E": "pe"}, years=10)
    if df.empty:
        return _empty(title, mode)
    sales = df[[c for c in ("P/S", "EV/Revenue") if c in df]]
    pe = df["P/E"] if "P/E" in df else pd.Series(dtype=float)
    bad = pe[(pe < 0) | (pe > PE_MAX)]
    pe_ok = pe.where((pe >= 0) & (pe <= PE_MAX))
    p = _pal(mode)

    has_pe = pe_ok.notna().any()
    note = "Year-end multiples."
    if len(bad):
        yrs = ", ".join(str(y) for y in bad.index)
        note += f" P/E hidden for {yrs} (negative or above {PE_MAX}x)."

    if has_pe and not sales.empty:
        fig = _two_panel("Price/sales and EV/revenue", "Price/earnings")
        _add_lines(fig, sales, p["series"][:2], ".1f", "x", row=1, col=1)
        _add_lines(fig, pe_ok.to_frame("P/E"), [p["series"][2]], ".1f", "x", row=1, col=2)
    else:
        # Only one family of multiples: a single panel, no empty half.
        fig = go.Figure()
        if has_pe:
            _add_lines(fig, pe_ok.to_frame("P/E"), [p["series"][2]], ".1f", "x")
        else:
            _add_lines(fig, sales, p["series"][:2], ".1f", "x")
            note += " No meaningful P/E (losses or extreme values)."
    fig.update_yaxes(ticksuffix="x", rangemode="tozero")
    _style(fig, title, note, SOURCE_FIN, mode)
    if has_pe and not sales.empty:
        _finish_two_panel(fig, mode)
    return fig


# ---------------------------------------------------------------------------
# 4. Returns and balance-sheet health
# ---------------------------------------------------------------------------

def returns_and_health(record: dict, mode: str = "light") -> go.Figure:
    """ROE / ROIC / ROA (%) left; current ratio and debt-to-equity (x) right.

    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: returns and balance-sheet health"
    ret = _frame(record, {"ROE": "roe", "ROIC": "roic", "ROA": "roa"}, years=10, scale=100)
    health = _frame(record, {"Current ratio": "currentRatio", "Debt/equity": "totalDebtToEquity"},
                    years=10)
    if ret.empty and health.empty:
        return _empty(title, mode)
    p = _pal(mode)
    both = not ret.empty and not health.empty
    if both:
        fig = _two_panel("Returns on equity, capital, assets", "Liquidity and leverage",
                         (0.55, 0.45))
    else:  # only one side has data: a single panel, no empty half
        fig = go.Figure()
    left = dict(row=1, col=1) if both else {}
    right = dict(row=1, col=2) if both else {}
    note = "Annual. Current ratio = current assets / current liabilities."
    if not ret.empty:
        _add_lines(fig, ret, p["series"][:3], ".1f", "%", **left)
        fig.update_yaxes(ticksuffix="%", **left)
        note += _clip_pct_axis(fig, ret, **left)
    if not health.empty:
        _add_lines(fig, health, [p["series"][3], p["muted"]], ".2f", "x", **right)
        fig.update_yaxes(ticksuffix="x", rangemode="tozero", **right)
    # Dashes keep lines readable where they coincide (e.g. ROIC = ROE with no debt).
    fig.update_traces(line_dash="dash", selector=dict(name="ROIC"))
    fig.update_traces(line_dash="dot", selector=dict(name="Debt/equity"))
    _style(fig, title, note, SOURCE_FIN, mode)
    if both:
        _finish_two_panel(fig, mode)
    return fig


# ---------------------------------------------------------------------------
# 5. Earnings surprises
# ---------------------------------------------------------------------------

def earnings_surprises(record: dict, mode: str = "light") -> go.Figure:
    """Actual vs estimated EPS, last 4 quarters. Beat = green, miss = red.

    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: earnings vs analyst estimates"
    recs = []
    for r in (record or {}).get("earnings") or []:
        a, e = _num(r.get("actual")), _num(r.get("estimate"))
        if math.isnan(a) and math.isnan(e):
            continue
        q, y = r.get("quarter"), r.get("year")
        recs.append(dict(period=str(r.get("period", "")),
                         label=f"Q{q} {y}" if q and y else str(r.get("period", "")),
                         actual=a, estimate=e, sp=_num(r.get("surprisePercent"))))
    if not recs:
        return _empty(title, mode)
    df = pd.DataFrame(recs).sort_values("period").tail(4)
    p = _pal(mode)
    known = df["actual"].notna() & df["estimate"].notna()
    status = ["n/a" if not k else "Beat" if a >= e else "Miss"
              for k, a, e in zip(known, df["actual"], df["estimate"])]
    color = {"Beat": p["good"], "Miss": p["bad"], "n/a": p["muted"]}
    symbol = {"Beat": "triangle-up", "Miss": "triangle-down", "n/a": "circle"}

    fig = go.Figure()
    # Stem from estimate to actual makes the size of the surprise visible.
    for _, r in df[known].iterrows():
        fig.add_trace(go.Scatter(x=[r["label"]] * 2, y=[r["estimate"], r["actual"]], mode="lines",
                                 line=dict(color=p["axis"], width=2), hoverinfo="skip",
                                 showlegend=False))
    fig.add_trace(go.Scatter(
        x=df["label"], y=df["estimate"], name="Analyst estimate", mode="markers",
        marker=dict(symbol="line-ew-open", size=24, color=p["muted"],
                    line=dict(width=3, color=p["muted"])),
        hovertemplate="<b>%{x}</b><br>Estimate: $%{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["label"], y=df["actual"], name="Actual EPS", mode="markers+text",
        marker=dict(size=15, color=[color[s] for s in status], symbol=[symbol[s] for s in status]),
        text=["" if s == "n/a" else f"{s} {fmt_pct(v, 0, signed=True)}"
              for s, v in zip(status, df["sp"])],
        textposition="middle right", textfont=dict(size=11, color=p["ink2"]), cliponaxis=False,
        customdata=list(zip(df["estimate"], df["sp"], status)),
        hovertemplate=("<b>%{x}</b> · %{customdata[2]}<br>Actual EPS: $%{y:.2f}"
                       "<br>Estimate: $%{customdata[0]:.2f}<br>Surprise: %{customdata[1]:+.1f}%"
                       "<extra></extra>"),
    ))
    fig.update_yaxes(tickprefix="$", tickformat=".2f", title_text="EPS (USD per share)")
    fig.update_xaxes(type="category", range=[-0.5, len(df) - 0.1])
    _style(fig, title, "Last 4 quarters. Triangle up = beat (green), down = miss (red).",
           SOURCE_MKT, mode, height=HEIGHT_SMALL)
    return fig


# ---------------------------------------------------------------------------
# 6. Analyst recommendations
# ---------------------------------------------------------------------------

RATINGS = [("strongBuy", "Strong buy"), ("buy", "Buy"), ("hold", "Hold"),
           ("sell", "Sell"), ("strongSell", "Strong sell")]


def analyst_recommendations(record: dict, mode: str = "light") -> go.Figure:
    """Stacked analyst rating counts per month, strong buy -> strong sell.

    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: analyst ratings"
    df = pd.DataFrame((record or {}).get("recommendations") or [])
    if df.empty or "period" not in df or not any(k in df for k, _ in RATINGS):
        return _empty(title, mode)
    df = df.sort_values("period")
    df["label"] = pd.to_datetime(df["period"], errors="coerce").dt.strftime("%b %Y")
    p = _pal(mode)
    colors = [p["good_strong"], p["good_soft"], p["neutral"], p["bad_soft"], p["bad"]]
    fig = go.Figure()
    for (key, label), c in zip(RATINGS, colors):
        if key not in df:
            continue
        fig.add_trace(go.Bar(
            x=df["label"], y=pd.to_numeric(df[key], errors="coerce"), name=label,
            marker=dict(color=c, line=dict(width=0)),
            hovertemplate=f"<b>{label}</b><br>%{{x}}: %{{y}} analysts<extra></extra>",
        ))
    fig.update_yaxes(title_text="Number of analysts", rangemode="tozero")
    fig.update_xaxes(type="category")
    _style(fig, title, "Count of analyst ratings, by month.", SOURCE_MKT, mode,
           height=HEIGHT_SMALL)
    # Stacked bars default to a reversed legend; keep it strong buy -> strong sell.
    fig.update_layout(barmode="stack", bargap=0.45, legend_traceorder="normal")
    return fig


# ---------------------------------------------------------------------------
# 7. KPI snapshot
# ---------------------------------------------------------------------------

def kpi_snapshot(record: dict, mode: str = "light") -> go.Figure:
    """Tile grid of TTM KPIs (values in the metrics block are already %).

    Input: one comparable record. Output: Figure (height 220).
    """
    title = f"{_name(record)}: key numbers today"
    m = (record or {}).get("metrics") or {}
    p = _pal(mode)
    ps, beta = _num(m.get("psTTM")), _num(m.get("beta"))
    growth = _num(m.get("revenueGrowthTTMYoy"))
    net = _num(m.get("netProfitMarginTTM"))
    ret52 = _num(m.get("52WeekPriceReturnDaily"))
    tiles = [  # (label, value text, signed value used for green/red, or None)
        ("Market cap", fmt_usd(_num(m.get("marketCapitalization")) * 1e6), None),
        ("Revenue growth", fmt_pct(growth, signed=True), growth),
        ("Gross margin", fmt_pct(m.get("grossMarginTTM")), None),
        ("Net margin", fmt_pct(net), net),
        ("Price / sales", "—" if math.isnan(ps) else f"{ps:.1f}x", None),
        ("Beta", "—" if math.isnan(beta) else f"{beta:.2f}", None),
        ("52-week price return", fmt_pct(ret52, signed=True), ret52),
    ]
    if all(v == "—" for _, v, _ in tiles):
        return _empty(title, mode)
    fig = go.Figure()
    cols = 4
    for i, (label, value, signed) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = c / cols, 1 - r * 0.55
        color = p["ink"]
        if signed is not None and not math.isnan(signed) and signed != 0:
            color = p["good_text"] if signed > 0 else p["bad"]
        fig.add_annotation(text=label, x=x, y=y, xref="paper", yref="paper", xanchor="left",
                           yanchor="top", showarrow=False, font=dict(size=12, color=p["muted"]))
        fig.add_annotation(text=f"<b>{value}</b>", x=x, y=y - 0.16, xref="paper", yref="paper",
                           xanchor="left", yanchor="top", showarrow=False,
                           font=dict(size=22, color=color))
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])
    _style(fig, title, "Trailing twelve months. Green / red = above / below zero.",
           SOURCE_MKT, mode, height=220, legend=False)
    fig.update_layout(margin=dict(t=72, b=36))
    fig.update_annotations(selector=dict(name="source"), yshift=-34)
    return fig


# ---------------------------------------------------------------------------
# 8. Portfolio comparables scatter
# ---------------------------------------------------------------------------

def portfolio_comparables_scatter(all_records: list[dict], highlight_company_id: str | None = None,
                                  mode: str = "light") -> go.Figure:
    """Bubble chart of every unique comparable: growth (x) vs gross margin (y), size = market cap.

    Input: the full list of records and the Company_ID of the startup to highlight.
    Output: Figure. Startups sharing a comparable (same ticker) share one bubble.
    """
    title = "Where each comparable sits: growth vs gross margin"
    by_ticker: dict[str, dict] = {}
    highlight = None
    for r in all_records or []:
        t = r.get("ticker")
        if not t:
            continue
        if r.get("Company_ID") == highlight_company_id:
            highlight = t
        m = r.get("metrics") or {}
        entry = by_ticker.setdefault(t, dict(
            ticker=t, name=r.get("display_name") or t, growth=_num(m.get("revenueGrowthTTMYoy")),
            gm=_num(m.get("grossMarginTTM")), mc=_num(m.get("marketCapitalization")), startups=[]))
        entry["startups"].append(r.get("Company_ID") or "?")
    df = pd.DataFrame(list(by_ticker.values()))
    if df.empty:
        return _empty(title, mode)
    df = df[df["growth"].notna() & df["gm"].notna()].reset_index(drop=True)
    if df.empty:
        return _empty(title, mode)
    if highlight:
        title = f"Where {highlight} sits among all comparables"
    p = _pal(mode)
    mc = df["mc"].fillna(df["mc"].median() if df["mc"].notna().any() else 1.0).clip(lower=0)
    root = mc ** 0.5  # bubble area ~ market cap
    size = 14 + 44 * (root - root.min()) / ((root.max() - root.min()) or 1)

    fig = go.Figure()
    # Highlight drawn first and semi-transparent, so a big bubble never hides a small one.
    for flag, name, color in ((True, "This startup's comparable", p["series"][0]),
                              (False, "Other comparables", p["neutral"])):
        sel = (df["ticker"] == highlight) == flag
        if not sel.any():
            continue
        d = df[sel]
        fig.add_trace(go.Scatter(
            x=d["growth"], y=d["gm"], mode="markers+text", name=name, text=d["ticker"],
            textposition="top center", cliponaxis=False,
            textfont=dict(size=13 if flag else 11, color=p["ink"] if flag else p["ink2"]),
            marker=dict(size=size[sel], color=color, opacity=0.75 if flag else 0.95,
                        line=dict(width=2, color=p["ink"] if flag else "rgba(0,0,0,0)")),
            customdata=list(zip(d["name"], [fmt_usd(v * 1e6) for v in d["mc"]],
                                [", ".join(s) for s in d["startups"]])),
            hovertemplate=("<b>%{customdata[0]} (%{text})</b><br>Revenue growth: %{x:+.1f}%"
                           "<br>Gross margin: %{y:.1f}%<br>Market cap: %{customdata[1]}"
                           "<br>Comparable for: %{customdata[2]}<extra></extra>"),
        ))
    xpad = (df["growth"].max() - df["growth"].min()) * 0.12 or 5
    ypad = (df["gm"].max() - df["gm"].min()) * 0.15 or 5
    fig.update_xaxes(title_text="Revenue growth, TTM vs prior year", ticksuffix="%",
                     showgrid=True, gridcolor=p["grid"], zeroline=True, zerolinecolor=p["axis"],
                     range=[df["growth"].min() - xpad, df["growth"].max() + xpad])
    fig.update_yaxes(title_text="Gross margin, TTM", ticksuffix="%",
                     range=[df["gm"].min() - ypad, df["gm"].max() + ypad])
    _style(fig, title, "Each bubble is one public comparable; bubble area = market cap.",
           SOURCE_MKT, mode, height=HEIGHT)
    fig.update_layout(margin=dict(b=74))
    fig.update_annotations(selector=dict(name="source"), yshift=-68)
    return fig


# ---------------------------------------------------------------------------
# 9. News volume
# ---------------------------------------------------------------------------

def news_volume(record: dict, mode: str = "light", days: int = 90) -> go.Figure:
    """Weekly count of news articles over the last ``days`` days of the data snapshot.

    The window ends at the record's ``fetched_at`` time (or the newest article), so the
    chart does not go empty when viewed long after the data was fetched.
    Input: one comparable record. Output: Figure.
    """
    title = f"{_name(record)}: news coverage per week"
    # Window arithmetic is done in UNIX seconds (avoids pd.Timedelta, which warns on
    # some pandas/NumPy combinations).
    secs = pd.Series([_num(n.get("datetime")) for n in (record or {}).get("news") or []],
                     dtype=float).dropna()
    if secs.empty:
        return _empty(title, mode)
    end_s = secs.max()
    fetched = pd.to_datetime((record or {}).get("fetched_at"), errors="coerce", utc=True)
    if not pd.isna(fetched):
        end_s = max(end_s, fetched.timestamp())
    start_s = end_s - days * 86400
    secs = secs[secs >= start_s]
    if secs.empty:
        return _empty(title, mode, f"No news articles in the last {days} days")
    ts = pd.to_datetime(secs, unit="s")
    start, end = pd.to_datetime(start_s, unit="s"), pd.to_datetime(end_s, unit="s")
    weeks = ts.dt.to_period("W-SUN").dt.start_time
    all_weeks = pd.period_range(start, end, freq="W-SUN").start_time
    counts = weeks.value_counts().reindex(all_weeks, fill_value=0).sort_index().astype(float)
    note = f"{len(ts)} articles, {start:%d %b} to {end:%d %b %Y}. First and last weeks are partial."
    first = ts.min()
    if (first - start).days > 14:
        # The feed is capped (busy tickers only return recent days): weeks before it
        # starts are unknown, not zero.
        counts[counts.index < first.to_period("W-SUN").start_time] = math.nan
        note = (f"{len(ts)} articles. The news feed only goes back to {first:%d %b %Y}; "
                "earlier weeks are not available.")
    p = _pal(mode)
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values, name="Articles", marker_color=p["series"][0],
        marker_line_width=0, customdata=[f"Week of {d:%d %b %Y}" for d in counts.index],
        hovertemplate="<b>%{customdata}</b><br>%{y} articles<extra></extra>",
    ))
    fig.update_xaxes(tickformat="%d %b", dtick=14 * 86400000)
    fig.update_yaxes(title_text="Articles", rangemode="tozero")
    _style(fig, title, note, SOURCE_MKT, mode, height=HEIGHT, legend=False)
    fig.update_layout(bargap=0.15)
    return fig
