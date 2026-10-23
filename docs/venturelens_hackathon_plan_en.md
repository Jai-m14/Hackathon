# VentureLens Hackathon Plan

You should choose **Option 4: A startup investor looking for high growth**. This direction is the easiest to turn into a complete product combining data analysis, AI explanations, and a clear allocation of funds.

## Recommended Product: VentureLens

### One-sentence positioning

> **VentureLens is an AI investment analyst for growth investors. It uses public financial data to create an explainable growth-oriented portfolio for $100,000.**

Because the challenge requires public data, do not claim that the tool directly invests in private startups. Instead, define the client as:

> An investor who uses publicly listed, high-growth companies as a public-market proxy for startup investing.

## The Five Required Sections

### 1. The Client

The client is an investor who:

- Has `$100,000` to invest
- Has an investment horizon of approximately five years
- Has a high risk tolerance
- Is targeting high growth
- Accepts significant volatility and the possibility of losing part of the principal
- Wants to know which companies to invest in, how much to allocate, and why

For the demo, use:

```text
Investment amount: $100,000
Time horizon: 5 years
Risk tolerance: High
Maximum position: 35%
Cash buffer: 10%
```

### 2. The Data

Recommended public data sources:

| Data | Source | Purpose |
|---|---|---|
| Revenue, gross margin, R&D, cash, operating cash flow | SEC EDGAR/XBRL | Assess growth, quality, and cash runway |
| Share price, market capitalisation, historical prices | Yahoo Finance / Twelve Data | Calculate valuation, volatility, and drawdown |
| Interest rates and inflation | FRED | Perform macroeconomic and valuation stress tests |
| Industry and macroeconomic growth | World Bank | Assess market opportunity |
| Annual reports, quarterly reports, and filing text | SEC filings | Provide evidence for the LLM's explanations |

For the live demo, prepare a CSV snapshot in advance rather than relying entirely on real-time APIs. This avoids network problems and API rate limits.

### 3. What the AI Does

The key design principle is:

> **Code performs the calculations; the LLM provides the explanation.**

Do not let the LLM directly decide the allocation. Judges may question a system that is not reproducible or controllable.

The code should:

- Clean the data
- Calculate revenue growth
- Calculate gross margin
- Estimate cash runway
- Calculate EV/Revenue
- Calculate volatility and risk penalties
- Generate investment scores
- Allocate the `$100,000`

The LLM should:

- Explain why a company is recommended
- Summarise the bull case and bear case
- Explain the main risks
- Identify what evidence would invalidate the recommendation
- Cite the relevant data sources

Recommended scoring formula:

$$
\text{FinalScore}
=
0.30G+0.20Q+0.15M+0.15S+0.10V-\text{RiskPenalty}
$$

Where:

- $G$: Growth
- $Q$: Business quality
- $M$: Market opportunity
- $S$: Financial survivability
- $V$: Valuation
- Risk Penalty: volatility, regulatory risk, cash burn, and other risks

### 4. The Recommendation: Where the Money Goes

The interface must clearly show the allocation:

| Company | Weight | Amount | Score |
|---|---:|---:|---:|
| Company A | 30% | $30,000 | 86.4 |
| Company B | 24% | $24,000 | 81.2 |
| Company C | 18% | $18,000 | 77.5 |
| Company D | 13% | $13,000 | 72.8 |
| Cash buffer | 15% | $15,000 | — |

You do not necessarily need to claim that the portfolio contains specific real companies. You can use:

- Real companies and publicly available data; or
- An anonymised demo dataset.

If you use real companies, clearly display:

- The data cut-off date
- The data sources
- That this is an educational prototype
- That it is not financial advice

### 5. Live Demo Flow

Aim for a three- to four-minute demo.

#### Opening: Introduce the problem

> Startup investors are not short of news. They are short of a fast, evidence-based way to decide which high-growth companies are worth the risk, how much to invest, and what evidence would invalidate the decision.

#### Step 1: Enter the investment objective

Show:

```text
Capital: $100,000
Horizon: 5 years
Risk tolerance: High
Maximum position: 35%
```

#### Step 2: Click “Analyse”

Show:

- Candidate rankings
- Overall score for each company
- Portfolio donut chart
- Investment amount for each company

Emphasise:

> The allocation is calculated deterministically. The LLM does not invent the numbers or decide the weights.

#### Step 3: Inspect one company

Show:

- Revenue growth
- Gross margin
- Cash runway
- EV/Revenue
- AI-generated investment explanation
- Main risks
- Conditions that would change the recommendation

#### Step 4: Run a stress test

For example, apply:

```text
Revenue growth: -20%
EV/Revenue multiple: -30%
Cash burn: +25%
```

Then show:

- Which companies lose allocation weight
- Which companies are removed from the portfolio
- Whether the cash buffer increases

## Suggested Team Roles

### Member 1: Data and modelling

Responsible for:

- CSV snapshot
- SEC/Yahoo Finance data integration
- Metric calculation
- Scoring model
- Portfolio allocation

### Member 2: Product interface

Responsible for:

- Streamlit interface
- Investor parameter panel
- Portfolio charts
- Company detail page
- Stress-testing interface

### Member 3: LLM and explanation layer

Responsible for:

- Structured JSON input
- Prompt design
- Evidence citations
- Bull and bear cases
- Risk summaries

### Member 4: Pitch and live demo

Responsible for:

- Three-minute demo script
- Product narrative
- Architecture diagram
- Disclaimer
- Backup plan for the live demo

## Minimum Viable Product

If time is limited, build only the following:

1. Data for 8–12 companies
2. 6–10 basic metrics
3. A deterministic scoring model
4. Automatic allocation of `$100,000`
5. One portfolio chart
6. An explanation card for each company
7. One simple stress test
8. Data sources and disclaimer

Do not start with:

- Full-web news scraping
- Complex multi-agent systems
- Real-time trading
- Automated order execution
- Complex forecasting models
- Private startup valuation prediction

These features add risk without necessarily improving your hackathon score.

## Pitch Closing

### English version

> **VentureLens is an evidence-first AI analyst for growth investors. It converts public filings and market data into a transparent $100,000 portfolio, separates calculation from explanation, and shows exactly what could invalidate the recommendation.**

### Chinese version

> VentureLens 是一个面向高增长投资人的证据优先 AI 分析师。它把公开披露和市场数据转化为透明的 $100,000 投资组合，把“怎么算”和“怎么解释”分开，并明确展示什么情况会推翻当前建议。
