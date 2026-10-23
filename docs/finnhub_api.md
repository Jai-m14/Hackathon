# Finnhub API Reference (for Claude)

Converted from the Finnhub API docs PDF (finnhub.io/docs/api, saved 23 Oct 2026). API keys in the code samples have been replaced with `YOUR_API_KEY`. Load the real key from `.env` (`FINNHUB_API_KEY`) and never hard-code it.

## Read this first

- **Base URL:** `https://finnhub.io/api/v1`
- **Auth:** pass `token=YOUR_API_KEY` as a query parameter, or the header `X-Finnhub-Token: YOUR_API_KEY`.
- **Python client:** `pip install finnhub-python`, then `finnhub_client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])`.
- **Rate limits:** the free plan allows about 60 calls/minute, plus a hard cap of 30 calls/second on every plan. Going over returns **HTTP 429**. Retry with backoff, and cache responses to disk.
- **Free vs Premium:** every section heading below is marked **(Free)** or **(Premium)**. Premium endpoints fail on a free key, so **don't build on them**.
- **Dates:** `from`/`to` arguments use `YYYY-MM-DD`. Timestamps in responses are UNIX seconds.
- **PDF conversion gaps:** some inline values were lost in the conversion and appear as blank gaps such as `Supporter values: , , .`. Known ones:
  - Peers `grouping`: `sector`, `industry`, `subIndustry` (default `industry`).
  - Basic Financials `metric`: use `all`.
  - Financials As Reported `freq`: `annual` or `quarterly`.
  If something is unclear, check the live docs at https://finnhub.io/docs/api.

## Free endpoints most useful for this project (company comparison)

| Purpose | Endpoint (REST path) | Python client |
|---|---|---|
| Find ticker by name | Symbol Lookup `/search?q=` | `symbol_lookup(q)` |
| Company profile (sector, country, IPO date, market cap) | Company Profile 2 `/stock/profile2?symbol=` | `company_profile2(symbol=...)` |
| Comparable companies | Peers `/stock/peers?symbol=&grouping=` | `company_peers(symbol)` |
| Key metrics + historical ratio series (margins, growth, valuation) | Basic Financials `/stock/metric?symbol=&metric=all` | `company_basic_financials(symbol, 'all')` |
| Multi-year financial statements (SEC, as reported) | Financials As Reported `/stock/financials-reported?symbol=&freq=` | `financials_reported(symbol=..., freq='annual')` |
| Recent earnings vs estimates | Earnings Surprises `/stock/earnings?symbol=` | `company_earnings(symbol)` |
| Analyst recommendation trends | Recommendation Trends `/stock/recommendation?symbol=` | `recommendation_trends(symbol)` |
| Company news (North America only; 1 year on free tier) | Company News `/company-news?symbol=&from=&to=` | `company_news(symbol, _from=..., to=...)` |
| Market news | Market News `/news?category=general` | `general_news('general')` |
| Recent and upcoming IPOs | IPO Calendar `/calendar/ipo?from=&to=` | `ipo_calendar(_from=..., to=...)` |
| Latest price | Quote `/quote?symbol=` | `quote(symbol)` |
| Insider sentiment | Insider Sentiment `/stock/insider-sentiment?symbol=&from=&to=` | `stock_insider_sentiment(symbol, from, to)` |

**Not free:** Stock Candles (price history; use yfinance or Twelve Data instead), Financial Statements (standardised), News Sentiment, Company ESG Scores, Revenue Estimates.


## Endpoint index

| Endpoint | Tier | Python client method |
|---|---|---|
| Trades - Last Price Updates | Free | - |
| News | Premium | - |
| Press Releases | Premium | - |
| Symbol Lookup | Free | `symbol_lookup` |
| Stock Symbol | Free | `stock_symbols` |
| Market Status | Free | `market_status` |
| Market Holiday | Free | `market_holiday` |
| Company Profile | Premium | `company_profile` |
| Company Profile 2 | Free | `company_profile2` |
| Company Executive | Premium | `company_executive` |
| Market News | Free | `general_news` |
| Company News | Free | `company_news` |
| Major Press Releases | Premium | `press_releases` |
| News Sentiment | Premium | `news_sentiment` |
| Peers | Free | `company_peers` |
| Basic Financials | Free | `company_basic_financials` |
| Ownership | Premium | `ownership` |
| Fund Ownership | Premium | `fund_ownership` |
| Institutional Profile | Premium | `institutional_profile` |
| Institutional Portfolio | Premium | `institutional_portfolio` |
| Institutional Ownership | Premium | `institutional_ownership` |
| Insider Transactions | Free | `stock_insider_transactions` |
| Insider Sentiment | Free | `stock_insider_sentiment` |
| Financial Statements | Premium | `financials` |
| Financials As Reported | Free | `financials_reported` |
| Revenue Breakdown | Premium | `stock_revenue_breakdown` |
| SEC Filings | Free | `filings` |
| SEC Sentiment Analysis | Premium | `sec_sentiment_analysis` |
| Similarity Index | Premium | `sec_similarity_index` |
| IPO Calendar | Free | `ipo_calendar` |
| Dividends | Premium | `stock_dividends` |
| Sector Metrics | Premium | `sector_metric` |
| Price Metrics | Premium | `price_metrics` |
| Symbol Change | Premium | `symbol_change` |
| ISIN Change | Premium | `isin_change` |
| Historical Market Cap | Premium | `historical_market_cap` |
| Historical Employee Count | Premium | `historical_employee_count` |
| Recommendation Trends | Free | `recommendation_trends` |
| Price Target | Premium | `price_target` |
| Stock Upgrade/Downgrade | Premium | `upgrade_downgrade` |
| Revenue Estimates | Premium | `company_revenue_estimates` |
| Earnings Estimates | Premium | `company_eps_estimates` |
| EBITDA Estimates | Premium | `company_ebitda_estimates` |
| EBIT Estimates | Premium | `company_ebit_estimates` |
| Net Income Estimates | Premium | `company_net_income_estimates` |
| Pretax Income Estimates | Premium | `company_pretax_income_estimates` |
| Gross Income Estimates | Premium | `company_gross_income_estimates` |
| DPS Estimates | Premium | `company_dps_estimates` |
| FCF Estimates | Premium | `company_fcf_estimates` |
| Capex Estimates | Premium | `company_capex_estimates` |
| OCF Estimates | Premium | `company_ocf_estimates` |
| Earnings Surprises | Free | `company_earnings` |
| Earnings Calendar | Free | `earnings_calendar` |
| Quote | Free | `quote` |
| Stock Candles | Premium | `stock_candles` |
| Delay | Free | `stock_tick` |
| Historical NBBO | Premium | `stock_nbbo` |
| Last Bid-Ask | Premium | `last_bid_ask` |
| Splits | Premium | `stock_splits` |
| Dividends 2 (Basic) | Premium | `stock_basic_dividends` |
| Indices Constituents | Premium | `indices_const` |
| ETFs Profile | Premium | `etfs_profile` |
| ETFs Holdings | Premium | `etfs_holdings` |
| ETFs Sector Exposure | Premium | `etfs_sector_exp` |
| ETFs Country Exposure | Premium | `etfs_country_exp` |
| ETFs Equity Allocation | Premium | `etfs_allocation` |
| Mutual Funds Profile | Premium | `mutual_fund_profile` |
| Mutual Funds Holdings | Premium | `mutual_fund_holdings` |
| Mutual Funds Sector Exposure | Premium | `mutual_fund_country_exp` |
| Mutual Funds EET | Premium | `mutual_fund_eet` |
| Mutual Funds EET PAI | Premium | `mutual_fund_eet_pai` |
| Bond Profile | Premium | `bond_profile` |
| US Government Bonds | Free | `bond_price` |
| Bond Tick Data | Premium | `bond_tick` |
| Bond Yield Curve | Premium | `bond_yield_curve` |
| List supported forex exchanges | Free | `forex_exchanges` |
| Forex Symbol | Free | `forex_symbols` |
| Forex Candles | Premium | `forex_candles` |
| Get rates for all forex pairs. Ideal for currency conversion | Free | `forex_rates` |
| List supported crypto exchanges | Free | `crypto_exchanges` |
| List supported crypto symbols by exchange | Free | `crypto_symbols` |
| Crypto Profile | Premium | `crypto_profile` |
| Crypto Candles | Premium | `crypto_candles` |
| Pattern Recognition | Premium | `pattern_recognition` |
| Support/Resistance | Premium | `support_resistance` |
| Aggregate Indicators | Premium | `aggregate_indicator` |
| Technical Indicators | Premium | `technical_indicator` |
| Earnings Call Transcripts List | Premium | `transcripts_list` |
| Earnings Call Transcripts | Premium | `transcripts` |
| Earnings Call Audio Live | Premium | `earnings_call_live` |
| Company Presentation | Premium | `stock_presentation` |
| Social Sentiment | Premium | `stock_social_sentiment` |
| Investment Themes (Thematic Investing) | Premium | `stock_investment_theme` |
| Supply Chain Relationships | Premium | `stock_supply_chain` |
| Company ESG Scores | Premium | `company_esg_score` |
| Historical ESG Scores | Premium | `company_historical_esg_score` |
| Profitability | Free | `company_earnings_quality_score` |
| USPTO Patents | Free | `stock_uspto_patent` |
| H1-B Visa Application | Free | `stock_visa_application` |
| Senate Lobbying | Free | `stock_lobbying` |
| USA Spending | Free | `stock_usa_spending` |
| Congressional Trading | Premium | `congressional_trading` |
| Bank Branch List | Premium | `bank_branch` |
| FDA Committee Meeting Calendar | Free | `fda_calendar` |
| AI Copilot | Premium | - |
| Revenue Breakdown & KPI | Premium | `stock_revenue_breakdown2` |
| Newsroom | Premium | `newsroom` |
| International Filings | Premium | `international_filings` |
| Global Filings Search | Premium | - |
| Search In Filing | Premium | - |
| Search Filter | Premium | - |
| Download Filings | Premium | - |
| Country Metadata | Free | `country` |
| Economic Calendar | Premium | `calendar_economic` |
| Economic Code | Premium | `economic_code` |
| Economic Data | Premium | `economic_data` |

---

## Trades - Last Price Updates (Free)

Stream real-time trades for US stocks, forex and crypto. Trades might not be available for some forex and crypto exchanges. In that case, a
price update will be sent with volume = 0. A message can contain multiple trades. 1 API key can only open 1 connection at a time.

The following FX brokers do not support streaming: FXCM, Forex.com, FHFX. To get latest price for FX, please use the Forex Candles or All
Rates endpoint.

**Response Attributes:**

type

Message type.

data

List of trades or price updates.

s
Symbol.

p
Last price.

t
UNIX milliseconds timestamp.

v
Volume.

c
List of trade conditions. A comprehensive list of trade conditions code can be found here

```python
#https://pypi.org/project/websocket_client/
import websocket
def on_message(ws, message):
    print(message)
def on_error(ws, error):
    print(error)
def on_close(ws):
   print("### closed ###")
def on_open(ws):
   ws.send('{"type":"subscribe","symbol":"AAPL"}')
   ws.send('{"type":"subscribe","symbol":"AMZN"}')
   ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
   ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')
if __name__ == "__main__":
   websocket.enableTrace(True)
   ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=YOUR_API_KEY",
                                        on_message = on_message,
                                        on_error = on_error,
                                        on_close = on_close)
   ws.on_open = on_open
   ws.run_forever()
```

Sample response:
```json
{
"data": [
    {
           "p": 7296.89,
           "s": "BINANCE:BTCUSDT",
           "t": 1575526691134,
           "v": 0.011467
    }
],
"type": "trade"
}
```

## News (Premium)

Stream real-time news for US and Canadian stocks.

**Response Attributes:**

type

Message type: .

data
List of news.

category
News category.

datetime
Published time in UNIX timestamp.

headline
News headline.

urlId
News ID.

image
Thumbnail image URL.

related
Related stocks and companies mentioned in the article.

source
News source.

summary
News summary.

url
URL of the original article.

```python
#https://pypi.org/project/websocket_client/
import websocket
def on_message(ws, message):
         print(message)
def on_error(ws, error):
         print(error)
def on_close(ws):
        print("### closed ###")
def on_open(ws):
        ws.send('{"type":"subscribe-news","symbol":"AAPL"}')
        ws.send('{"type":"subscribe-news","symbol":"AMZN"}')
        ws.send('{"type":"subscribe-news","symbol":"MSFT"}')
        ws.send('{"type":"subscribe-news","symbol":"BYND"}')
if __name__ == "__main__":
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=YOUR_API_KEY",
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()
```

Sample response:
```json
{
"data": [
         {
            "category": "company",
            "datetime": 1679920200,
            "headline": "CanAlaska Uranium Announces Airborne Electromagnetic Survey Completed at Geikie Project in Athabasca
Basin",
            "id": 119440189,
            "image": "https://media.zenfs.com/en/newsfile_64/0522ee5d9e134e6f966c6ecdfc50fb46",
           "related": "CVVUF",
           "source": "Yahoo",
           "summary": "Multiple Priority Targets Associated with Regional Scale Fault Structures Preparation Underway for First
Drill ProgramDrilling Continues at West McArthur JV and Key Extension ProjectsVancouver, British Columbia--(Newsfile Corp. -
March 27, 2023) - CanAlaska Uranium Ltd. (TSXV: CVV) (OTCQX: CVVUF) (FSE: DH7N) (\"CanAlaska\" or the \"Company\") is
pleased to announce completion of a high-resolution airborne Versatile Time Domain Electromagnetic (\"VTEM Plus\") survey on
it's 60%-owned Geikie project in",
"url": "https://finance.yahoo.com/news/canalaska-uranium-announces-airborne-electromagnetic-123000318.html"
}
],
"type": "news"
}
```

## Press Releases (Premium)

Stream real-time press releases data for global companies. This feature is only available for Enterprise users.

**Response Attributes:**

type

Message type: .

data

List of news.

datetime
Published time in UNIX timestamp.

headline
News headline.

symbol
Related stocks and companies mentioned in the article.

fullText
URL to download the full-text data.

url
URL to read the article.

```python
#https://pypi.org/project/websocket_client/
import websocket
def on_message(ws, message):
  print(message)
def on_error(ws, error):
  print(error)
def on_close(ws):
 print("### closed ###")
def on_open(ws):
 ws.send('{"type":"subscribe-pr","symbol":"AAPL"}')
 ws.send('{"type":"subscribe-pr","symbol":"AMZN"}')
 ws.send('{"type":"subscribe-pr","symbol":"MSFT"}')
 ws.send('{"type":"subscribe-pr","symbol":"BYND"}')
if __name__ == "__main__":
 websocket.enableTrace(True)
 ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=YOUR_API_KEY",
                             on_message = on_message,
                             on_error = on_error,
                             on_close = on_close)
 ws.on_open = on_open
 ws.run_forever()
```

Sample response:
```json
{
"data": [
  {
     "datetime": 1637696940,
     "fullText": "https://static2.finnhub.io/file/publicdatany/
pr/0eb7fb4118ec53204755719b4cc4d57e9370d3caa2fa15d5e7a8f3b4d99cc881.html",
     "headline": "STOCKHOLDER ALERT: Monteverde &amp; Associates PC Continues to Investigate the Following Merger",
     "symbol": "PAE,ZIXI,KRA",
     "url": "https://finnhub.io/api/press-releases?id=0eb7fb4118ec53204755719b4cc4d57e9370d3caa2fa15d5e7a8f3b4d99cc881"
 }
],
"type": "pr"
}
```

## Symbol Lookup (Free)

Python client: `finnhub_client.symbol_lookup(...)`

Search for best-matching symbols based on your query. You can input anything from symbol, security's name to ISIN and Cusip.

**Arguments:**

q *(REQUIRED)*
Query text can be symbol, name, isin, or cusip.

exchange *(optional)*
Exchange limit.

**Response Attributes:**

count
Number of results.

result
Array of search results.

description
Symbol description

displaySymbol
Display symbol name.

symbol endpoint.
Unique symbol used to identify this symbol used in

type
Security type.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.symbol_lookup('apple'))
```

Sample response:
```json
. A list of supported
{
"count": 4,
"result": [
    {
       "description": "APPLE INC",
       "displaySymbol": "AAPL",
       "symbol": "AAPL",
       "type": "Common Stock"
    },
   {
      "description": "APPLE INC",
      "displaySymbol": "AAPL.SW",
      "symbol": "AAPL.SW",
      "type": "Common Stock"
   },
   {
      "description": "APPLE INC",
      "displaySymbol": "APC.BE",
      "symbol": "APC.BE",
      "type": "Common Stock"
   },
   {
      "description": "APPLE INC",
      "displaySymbol": "APC.DE",
      "symbol": "APC.DE",
      "type": "Common Stock"
   }
]
}
```

## Stock Symbol (Free)

Python client: `finnhub_client.stock_symbols(...)`

List supported stocks. We use the following symbology to identify stocks on Finnhub
exchange codes can be found here.

**Arguments:**

exchange *(REQUIRED)*
Exchange you want to get the list of symbols from. List of exchange codes can be found here.

mic *(optional)*
Filter by MIC code.

securityType *(optional)*
Filter by security type used by OpenFigi standard.

currency *(optional)*
Filter by currency.

**Response Attributes:**

currency
Price's currency. This might be different from the reporting currency of fundamental data.
description
Symbol description
displaySymbol

Display symbol name.

figi

FIGI identifier.

isin
ISIN. This field is only available for EU stocks and selected Asian markets. Entitlement from Finnhub is required to access this field.

mic
Primary exchange's MIC.

shareClassFIGI
Global Share Class FIGI.

symbol endpoint.
Unique symbol used to identify this symbol used in

symbol2
Alternative ticker for exchanges with multiple tickers for 1 stock such as BSE.

type
Security type.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_symbols('US'))
```

Sample response:
```json
[
{
    "currency": "USD",
    "description": "UAN POWER CORP",
    "displaySymbol": "UPOW",
    "figi": "BBG000BGHYF2",
    "mic": "OTCM",
    "symbol": "UPOW",
    "type": "Common Stock"
},
{
   "currency": "USD",
   "description": "APPLE INC",
   "displaySymbol": "AAPL",
   "figi": "BBG000B9Y5X2",
   "mic": "XNGS",
   "symbol": "AAPL",
   "type": "Common Stock"
},
{
   "currency": "USD",
   "description": "EXCO TECHNOLOGIES LTD",
   "displaySymbol": "EXCOF",
   "figi": "BBG000JHDDS8",
   "mic": "OOTC",
   "symbol": "EXCOF",
   "type": "Common Stock"
}
]
```

## Market Status (Free)

Python client: `finnhub_client.market_status(...)`

Get current market status for global exchanges (whether exchanges are open or close).

**Arguments:**

exchange *(REQUIRED)*
Exchange code.

**Response Attributes:**

exchange
Exchange.

holiday
Holiday event.

isOpen
Whether the market is open at the moment.

session

Market session. Can be 1 of the following values: , , or if the market is closed.

t
Current timestamp.

timezone
Timezone.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.market_status(exchange='US'))
```

Sample response:
```json
{
"exchange": "US",
"holiday": null,
"isOpen": false,
"session": "pre-market",
"timezone": "America/New_York",
"t": 1697018041
}
```

## Market Holiday (Free)

Python client: `finnhub_client.market_holiday(...)`

Get a list of holidays for global exchanges.

**Arguments:**

exchange *(REQUIRED)*
Exchange code.

**Response Attributes:**

data
Array of holidays.

atDate
Date.

eventName
Holiday's name.

tradingHour
Trading hours for this day if the market is partially closed only.

exchange
Exchange.

timezone
Timezone.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.market_holiday(exchange='US'))
```

Sample response:
```json
{
"data": [
    {
       "eventName": "Christmas",
       "atDate": "2023-12-25",
       "tradingHour": ""
    },
    {
       "eventName": "Independence Day",
      "atDate": "2023-07-03",
      "tradingHour": "09:30-13:00"
   }
],
"exchange": "US",
"timezone": "America/New_York"
}
```

## Company Profile (Premium)

Python client: `finnhub_client.company_profile(...)`

Get general information of a company. You can query by symbol, ISIN or CUSIP

**Arguments:**

symbol *(optional)*
Symbol of the company: AAPL e.g.

isin *(optional)*
ISIN

cusip *(optional)*
CUSIP

**Response Attributes:**

address
Address of company's headquarter.
alias
Company name alias.
city
City of company's headquarter.
country
Country of company's headquarter.
currency
Currency used in company filings and financials.
cusip
CUSIP number.
description
Company business summary.
employeeTotal
Number of employee.
estimateCurrency
Currency used in Estimates data.
exchange
Listed exchange.
finnhubIndustry
Finnhub industry classification.
ipo
IPO date.
irUrl
Investor relations website.
isin
ISIN number.
lei
LEI number.
logo
Logo image.

marketCapCurrency

Currency used in market capitalization.

marketCapitalization
Market Capitalization.

naics
NAICS industry.

naicsNationalIndustry
NAICS national industry.

naicsSector
NAICS sector.

naicsSubsector
NAICS subsector.

name
Company name.

phone
Company phone number.

sedol
Sedol number.

shareOutstanding
Number of oustanding shares.

state
State of company's headquarter.

ticker
Company symbol/ticker as used on the listed exchange.

weburl
Company website.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_profile(symbol='AAPL'))
```

Sample response:
```json
{
"address": "1 Apple Park Way",
"city": "CUPERTINO",
"country": "US",
"currency": "USD",
"cusip": "",
"sedol":"2046251",
"description": "Apple Inc. is an American multinational technology company headquartered in Cupertino, California, that
designs, develops, and sells consumer electronics, computer software, and online services. It is considered one of the Big
Four technology companies, alongside Amazon, Google, and Microsoft. The company's hardware products include the iPhone
smartphone, the iPad tablet computer, the Mac personal computer, the iPod portable media player, the Apple Watch smartwatch,
the Apple TV digital media player, the AirPods wireless earbuds and the HomePod smart speaker. Apple's software includes the
macOS, iOS, iPadOS, watchOS, and tvOS operating systems, the iTunes media player, the Safari web browser, the Shazam
acoustic fingerprint utility, and the iLife and iWork creativity and productivity suites, as well as professional
applications like Final Cut Pro, Logic Pro, and Xcode. Its online services include the iTunes Store, the iOS App Store, Mac
App Store, Apple Music, Apple TV+, iMessage, and iCloud. Other services include Apple Store, Genius Bar, AppleCare, Apple
Pay, Apple Pay Cash, and Apple Card.",
"employeeTotal": "137000",
"exchange": "NASDAQ/NMS (GLOBAL MARKET)",
"ipo": "1980-12-12",
"isin": "",
"marketCapitalization": 1415993,
"naics": "Communications Equipment Manufacturing",
"naicsNationalIndustry": "Radio and Television Broadcasting and Wireless Communications Equipment Manufacturing",
"naicsSector": "Manufacturing",
"naicsSubsector": "Computer and Electronic Product Manufacturing",
"name": "Apple Inc",
"phone": "14089961010",
"shareOutstanding": 4375.47998046875,
"state": "CALIFORNIA",
"ticker": "AAPL",
"weburl": "https://www.apple.com/",
"logo": "https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
"finnhubIndustry":"Technology"
}
```

## Company Profile 2 (Free)

Python client: `finnhub_client.company_profile2(...)`

Get general information of a company. You can query by symbol, ISIN or CUSIP. This is the free version of Company Profile.

**Arguments:**

symbol *(optional)*
Symbol of the company: AAPL e.g.

isin *(optional)*
ISIN

cusip *(optional)*
CUSIP

**Response Attributes:**

country
Country of company's headquarter.
currency

Currency used in company filings.

exchange
Listed exchange.

finnhubIndustry
Finnhub industry classification.

ipo
IPO date.

logo
Logo image.

marketCapitalization
Market Capitalization.

name
Company name.

phone
Company phone number.

shareOutstanding
Number of oustanding shares.

ticker
Company symbol/ticker as used on the listed exchange.

weburl
Company website.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_profile2(symbol='AAPL'))
```

Sample response:
```json
{
"country": "US",
"currency": "USD",
"exchange": "NASDAQ/NMS (GLOBAL MARKET)",
"ipo": "1980-12-12",
"marketCapitalization": 1415993,
"name": "Apple Inc",
"phone": "14089961010",
"shareOutstanding": 4375.47998046875,
"ticker": "AAPL",
"weburl": "https://www.apple.com/",
"logo": "https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
"finnhubIndustry":"Technology"
}
```

## Company Executive (Premium)

Python client: `finnhub_client.company_executive(...)`

Get a list of company's executives and members of the Board.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

**Response Attributes:**

executive
Array of company's executives and members of the Board.
age
Age
compensation
Total compensation
currency
Compensation currency
name
Executive name
sex
Sex
since
Year first appointed as executive/director of the company
title
Title
symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_executive('AAPL'))
```

Sample response:
```json
{
"executive": [
    {
       "age": 56,
       "compensation": 25209637,
       "currency": "USD",
       "name": "Luca Maestri",
       "position": "Senior Vice President and Chief Financial Officer",
       "sex": "male",
      "since": "2014"
   },
   {
      "age": 59,
      "compensation": 11555466,
      "currency": "USD",
      "name": "Mr. Timothy Cook",
      "position": "Director and Chief Executive Officer",
      "sex": "male",
      "since": "2011"
   }
]
}
```

## Market News (Free)

Python client: `finnhub_client.general_news(...)`

Get latest market news.

**Arguments:**

category *(REQUIRED)*

This parameter can be 1 of the following values .

minId *(optional)*
Use this field to get only news after this ID. Default to 0

**Response Attributes:**

category
News category.

datetime
Published time in UNIX timestamp.

headline
News headline.

id params to get the latest news only.
News ID. This value can be used for

image
Thumbnail image URL.

related
Related stocks and companies mentioned in the article.

source
News source.

summary

News summary.

url
URL of the original article.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.general_news('general', min_id=0))
```

Sample response (truncated):
```json
[
{
      "category": "technology",
      "datetime": 1596589501,
      "headline": "Square surges after reporting 64% jump in revenue, more customers using Cash App",
      "id": 5085164,
      "image": "https://image.cnbcfm.com/api/v1/image/105569283-1542050972462rts25mct.jpg?v=1542051069",
      "related": "",
      "source": "CNBC",
     "summary": "Shares of Square soared on Tuesday evening after posting better-than-expected quarterly results and strong
growth in its consumer payments app.",
     "url": "https://www.cnbc.com/2020/08/04/square-sq-earnings-q2-2020.html"
},
{
     "category": "business",
     "datetime": 1596588232,
     "headline": "B&G Foods CEO expects pantry demand to hold up post-pandemic",
     "id": 5085113,
     "image": "https://image.cnbcfm.com/api/v1/image/106629991-1595532157669-gettyimages-1221952946-362857076_1-5.jpeg?
v=1595532242",
     "related": "",
     "source": "CNBC",
     "summary": "\"I think post-Covid, people will be working more at home, which means people will be eating more
breakfast\" and other meals at home, B&G CEO Ken Romanzi said.",
     "url": "https://www.cnbc.com/2020/08/04/bg-foods-ceo-expects-pantry-demand-to-hold-up-post-pandemic.html"
},
{
     "category": "top news",
     "datetime": 1596584406,
     "headline": "Anthony Levandowski gets 18 months in prison for stealing Google self-driving car files",
     "id": 5084850,
     "image": "https://image.cnbcfm.com/api/v1/image/106648265-1596584130509-UBER-LEVANDOWSKI.JPG?v=1596584247",
     "related": "",
     "source": "CNBC",
     "summary": "A U.S. judge on Tuesday sentenced former Google engineer Anthony Levandowski to 18 months in prison for
stealing a trade secret from Google related to self-driving cars months before becoming the head of Uber Technologies Inc's
rival unit.",
"url": "https://www.cnbc.com/2020/08/04/anthony-levandowski-gets-18-months-in-prison-for-stealing-google-self-driving-car-
files.html"
}
...
```

## Company News (Free)

Python client: `finnhub_client.company_news(...)`

List latest company news by symbol. This endpoint is only available for North American companies.
Free Tier: 1 year of historical news and new updates

**Arguments:**

symbol *(REQUIRED)*

Company symbol.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

category
News category.

datetime
Published time in UNIX timestamp.

headline
News headline.

id params to get the latest news only.
News ID. This value can be used for

image
Thumbnail image URL.

related
Related stocks and companies mentioned in the article.

source
News source.

summary
News summary.

url
URL of the original article.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_news('AAPL', _from="2020-06-01", to="2020-06-10"))
```

Sample response (truncated):
```json
[
{
              "category": "company news",
              "datetime": 1569550360,
              "headline": "More sops needed to boost electronic manufacturing: Top govt official More sops needed to boost electronic
manufacturing: Top govt official. More sops needed to boost electronic manufacturing: Top govt official More sops needed to
boost electronic manufacturing: Top govt official",
              "id": 25286,
              "image": "https://img.etimg.com/thumb/msid-71321314,width-1070,height-580,imgsize-481831,overlay-economictimes/
photo.jpg",
             "related": "AAPL",
             "source": "The Economic Times India",
             "summary": "NEW DELHI | CHENNAI: India may have to offer electronic manufacturers additional sops such as cheap credit
and incentives for export along with infrastructure support in order to boost production and help the sector compete with
China, Vietnam and Thailand, according to a top government official.These incentives, over and above the proposed reduction
of corporate tax to 15% for new manufacturing units, are vital for India to successfully attract companies looking to
relocate manufacturing facilities."While the tax announcements made last week send a very good signal, in order to help
attract investments, we will need additional initiatives," the official told ET, pointing out that Indian electronic
manufacturers incur 8-10% higher costs compared with other Asian countries.Sops that are similar to the incentives for
export under the existing Merchandise Exports from India Scheme (MEIS) are what the industry requires, the person said.MEIS
gives tax credit in the range of 2-5%. An interest subvention scheme for cheaper loans and a credit guarantee scheme for
plant and machinery are some other possible measures that will help the industry, the official added."This should be 2.0
(second) version of the electronic manufacturing cluster (EMC) scheme, which is aimed at creating an ecosystem with an
anchor company plus its suppliers to operate in the same area," he said.Last week, finance minister Nirmala Sitharaman
announced a series of measures to boost economic growth including a scheme allowing any new manufacturing company
incorporated on or after October 1, to pay income tax at 15% provided the company does not avail of any other exemption or
incentives.",
             "url": "https://economictimes.indiatimes.com/industry/cons-products/electronics/more-sops-needed-to-boost-electronic-
manufacturing-top-govt-official/articleshow/71321308.cms"
},
{
             "category": "company news",
             "datetime": 1569528720,
             "headline": "How to disable comments on your YouTube videos in 2 different ways",
             "id": 25287,
"image": "https://amp.businessinsider.com/images/5d8d16182e22af6ab66c09e9-1536-768.jpg",
"related": "AAPL",
"source": "Business Insider",
"summary": "You can disable comments on your own YouTube video if you don't want people to comment on it. It's easy to
disable comments on YouTube by adjusting the settings for one of your videos in the beta or classic version of YouTube Studio.
...
```

## Major Press Releases (Premium)

Python client: `finnhub_client.press_releases(...)`

Get latest major press releases of a company. This data can be used to highlight the most significant events comprised of mostly press
releases sourced from the exchanges, BusinessWire, AccessWire, GlobeNewswire, Newsfile, and PRNewswire.

Full-text press releases data is available for Enterprise clients. Contact Us to learn more.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

from *(optional)*
From time: 2020-01-01.

to *(optional)*
To time: 2020-01-05.

**Response Attributes:**

majorDevelopment
Array of major developments.

datetime format.
Published time in

description
Development description.

headline
Development headline.

symbol
Company symbol.

url
URL.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.press_releases('AAPL'))
```

Sample response:
```json
{
"majorDevelopment": [
         {
            "symbol": "AAPL",
            "datetime": "2020-08-04 17:06:32",
            "headline": "27-inch iMac Gets a Major Update",
            "description": "CUPERTINO, Calif.--(BUSINESS WIRE)-- Apple today announced a major update to its 27-inch iMac�. By far
the most powerful and capable iMac ever, it features faster Intel processors up to 10 cores, double the memory capacity,
next-generation AMD graphics, superfast SSDs across the line with four times the storage capacity, a new nano-texture glass
option for an even more stunning Retina� 5K display, a 1080p FaceTime� HD camera, higher fidelity speakers, and studio-
quality mics. For the consumer using their iMac all day, every day, to the aspiring creative looking for inspiration, to the
serious pro pushing the limits of their creativity, the new 27-inch iMac delivers the ultimate desktop experience that is
now better in every way."
        },
        {
           "symbol": "AAPL",
           "datetime": "2020-03-28 09:41:23",
"headline": "Apple Central World Opens Friday in Thailand",
"description": "BANGKOK--(BUSINESS WIRE)-- Apple� today previewed Apple Central World, its second and largest retail
location in Thailand. Nestled in the heart of Ratchaprasong, Bangkok's iconic intersection, the store provides a completely new
and accessible destination within the lively city. Apple Central World's distinctive architecture is brought to life with the
first-ever all-glass design, housed under a cantilevered Tree Canopy roof. Once inside, customers can travel between two levels
via a spiral staircase that wraps around a timber core, or riding a unique cylindrical elevator clad in mirror-polished
stainless steel. Guests can enter from the ground or upper level, which provides a direct connection to the Skytrain and the
city's largest shopping center. The outdoor plaza offers a place for the community to gather, with benches and large Terminalia
trees surrounding the space."
}
],
"symbol": "AAPL"
}
```

## News Sentiment (Premium)

Python client: `finnhub_client.news_sentiment(...)`

Get company's news sentiment and statistics. This endpoint is only available for US companies.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

**Response Attributes:**

buzz
Statistics of company news in the past week.
articlesInLastWeek
buzz
weeklyAverage
companyNewsScore
News score.
sectorAverageBullishPercent
Sector average bullish percent.

sectorAverageNewsScore

Sectore average score.

sentiment
News sentiment.

bearishPercent

bullishPercent

symbol
Requested symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.news_sentiment('AAPL'))
```

Sample response:
```json
{
"buzz": {
    "articlesInLastWeek": 20,
    "buzz": 0.8888,
    "weeklyAverage": 22.5
},
"companyNewsScore": 0.9166,
"sectorAverageBullishPercent": 0.6482,
"sectorAverageNewsScore": 0.5191,
"sentiment": {
   "bearishPercent": 0,
   "bullishPercent": 1
},
"symbol": "V"
}
```

## Peers (Free)

Python client: `finnhub_client.company_peers(...)`

Get company peers. Return a list of peers operating in the same country and sector/industry.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

grouping *(optional)*

Specify the grouping criteria for choosing peers.Supporter values: , , . Default to .

**Response Attributes:**

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_peers('AAPL'))
```

Sample response:
```json
[
"AAPL",
"EMC",
"HPQ",
"DELL",
"WDC",
"HPE",
"NTAP",
"CPQ",
"SNDK",
"SEG"
]
```

## Basic Financials (Free)

Python client: `finnhub_client.company_basic_financials(...)`

Get company basic financials such as margin, P/E ratio, 52-week high/low etc.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

metric *(REQUIRED)*
Metric type. Can be 1 of the following values

**Response Attributes:**

metric
Map key-value pair of key ratios and metrics.
metricType
Metric type.
series
Map key-value pair of time-series ratios.
symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_basic_financials('AAPL', 'all'))
```

Sample response (truncated):
```json
{
    "series": {
    "annual": {
       "currentRatio": [
          {
             "period": "2019-09-28",
             "v": 1.5401
          },
          {
            "period": "2018-09-29",
            "v": 1.1329
         }
      ],
      "salesPerShare": [
         {
            "period": "2019-09-28",
            "v": 55.9645
         },
         {
            "period": "2018-09-29",
            "v": 53.1178
         }
      ],
      "netMargin": [
         {
            "period": "2019-09-28",
            "v": 0.2124
         },
         {
            "period": "2018-09-29",
            "v": 0.2241
         }
      ]
   }
},
"metric": {
   "10DayAverageTradingVolume": 32.50147,
   "52WeekHigh": 310.43,
   "52WeekLow": 149.22,
   "52WeekLowDate": "2019-01-14",
...
```

## Ownership (Premium)

Python client: `finnhub_client.ownership(...)`

Get a full list of shareholders of a company in descending order of the number of shares held. Data is sourced from ,

and for US market, for UK market, for Canadian market and equivalent filings for other international markets.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

limit *(optional)*

Limit number of results. Leave empty to get the full list.

**Response Attributes:**

ownership
Array of investors with detailed information about their holdings.

change
Number of share changed (net buy or sell) from the last period.

filingDate
Filing date.

name
Investor's name.

share
Number of shares held by the investor.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.ownership('AAPL', limit=5))
```

Sample response:
```json
{
"ownership": [
    {
       "name": "The Vanguard Group, Inc.",
       "share": 329323420,
       "change": -1809077,
       "filingDate": "2019-12-31"
    },
    {
      "name": "BRK.A | Berkshire Hathaway Inc.",
      "share": 245155570,
      "change": -3683113,
      "filingDate": "2019-12-31"
   },
   {
      "name": "BlackRock Institutional Trust Co NA",
      "share": 187354850,
      "change": -2500563,
      "filingDate": "2020-03-31"
   }
],
"symbol": "AAPL"
}
```

## Fund Ownership (Premium)

Python client: `finnhub_client.fund_ownership(...)`

Get a full list fund and institutional investors of a company in descending order of the number of shares held. Data is sourced from ,

and for US market, for UK market, for Canadian market and equivalent filings for other

international markets.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

limit *(optional)*
Limit number of results. Leave empty to get the full list.

**Response Attributes:**

ownership
Array of investors with detailed information about their holdings.

change
Number of share changed (net buy or sell) from the last period.

filingDate
Filing date.

name
Investor's name.

portfolioPercent
Percent of the fund's portfolio comprised of the company's share.

share
Number of shares held by the investor.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.fund_ownership('AAPL', limit=5))
```

Sample response:
```json
{
"ownership": [
    {
       "name": "AGTHX | American Funds Growth Fund of America",
       "share": 5145353,
       "change": 57427,
       "filingDate": "2020-03-31",
       "portfolioPercent": 1.88
    },
   {
      "name": "Vanguard Total Stock Market Index Fund",
      "share": 4227464,
      "change": 73406,
      "filingDate": "2020-03-31",
      "portfolioPercent": 0.45
   },
   {
      "name": "ANWPX | American Funds New Perspective",
      "share": 3377612,
      "change": 0,
      "filingDate": "2020-03-31",
      "portfolioPercent": 2.64
   }
],
"symbol": "TSLA"
}
```

## Institutional Profile (Premium)

Python client: `finnhub_client.institutional_profile(...)`

Get a list of well-known institutional investors. Currently support 60+ profiles.

**Arguments:**

cik *(optional)*
Filter by CIK. Leave blank to get the full list.

**Response Attributes:**

cik
CIK.

data
Array of investors.

cik
Investor's company CIK.

firmType
Firm type.

manager
Manager.

philosophy
Investing philosophy.

profile
Profile info.

profileImg

Profile image.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.institutional_profile()
```

Sample response:
```json
{
"cik": "1067983",
"data": [
        {
           "cik": "1067983",
           "firmType": "Institutional Investment Manager",
           "manager": "Warren Buffett",
           "philosophy": "Value investing is the hallmark of Warren Buffett's investment approach. By choosing stocks whose share
price is below their intrinsic or book value, value investors can increase their returns. This suggests that the stock will
increase in value going forward and that the market is now undervaluing it. Only enterprises that Buffett is familiar with
are chosen for investment by Berkshire, and a safety margin is always required.",
          "profile": "Warren Edward Buffett (born August 30, 1930) is an American business magnate, investor, and
philanthropist. He is currently the chairman and CEO of Berkshire Hathaway. He is one of the most successful investors in
the world and has a net worth of over $103 billion as of August 2022, making him the world's seventh-wealthiest person. Buffett
has been the chairman and largest shareholder of Berkshire Hathaway since 1970. He has been referred to as the \"Oracle\" or
\"Sage\" of Omaha by global media. He is noted for his adherence to value investing, and his personal frugality despite his
immense wealth. Buffett is a philanthropist, having pledged to give away 99 percent of his fortune to philanthropic causes,
primarily via the Bill \u0026 Melinda Gates Foundation. He founded The Giving Pledge in 2010 with Bill Gates, whereby
billionaires pledge to give away at least half of their fortunes.",
"profileImg": "https://static4.finnhub.io/file/publicdatany5/guru_profile_pic/1067983.jpg"
}
]
}
```

## Institutional Portfolio (Premium)

Python client: `finnhub_client.institutional_portfolio(...)`

Get the holdings/portfolio data of institutional investors from 13-F filings. Limit to 1 year of data at a time. You can get a list of supported CIK
here.

**Arguments:**

cik *(REQUIRED)*
Fund's CIK.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

cik

CIK.

data

Array of positions.

filingDate
Filing date.

portfolio
Array of positions.

change
Number of shares change.

cusip
CUSIP.

name
Position's name.

noVoting
Number of shares with no voting rights.

percentage
Percentage of portfolio.

putCall for options.
or

share
Number of shares.

sharedVoting
Number of shares with shared voting rights.

soleVoting
Number of shares with sole voting rights.

symbol
Symbol.

value
Position value.

reportDate
Report date.

name
Investor's name.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.institutional_portfolio(cik="1000097", _from="2022-10-01", to="2022-10-11"))
```

Sample response:
```json
{
"cik": "1000097",
"data": [
       {
          "filingDate": "2022-06-30",
          "portfolio": [
           {
                "change": -41600,
                "name": "ABBOTT LABS",
               "noVoting": 0,
               "percentage": 0,
               "putCall": "",
               "share": 0,
               "sharedVoting": 0,
               "soleVoting": 41600,
               "symbol": "ABT",
               "value": 0
          },
          {
               "change": -275000,
               "name": "ADICET BIO INC",
               "noVoting": 0,
               "percentage": 0,
               "putCall": "",
               "share": 0,
               "sharedVoting": 0,
               "soleVoting": 275000,
               "symbol": "ACET",
               "value": 0
          }
         ],
         "reportDate": "2022-06-30"
      }
],
"name": "KINGDON CAPITAL MANAGEMENT, L.L.C."
}
```

## Institutional Ownership (Premium)

Python client: `finnhub_client.institutional_ownership(...)`

Get a list institutional investors' positions for a particular stock overtime. Data from 13-F filings. Limit to 1 year of data at a time.

**Arguments:**

symbol *(REQUIRED)*
Filter by symbol.

cusip *(REQUIRED)*
Filter by CUSIP.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

cusip

Cusip.

data

Array of institutional investors.

ownership
Array of institutional investors.

change
Number of shares change.

cik
Investor's company CIK.

name
Firm's name.

noVoting
Number of shares with no voting rights.

percentage
Percentage of portfolio.

putCall for options.
or

share
News score.

sharedVoting
Number of shares with shared voting rights.

soleVoting
Number of shares with sole voting rights.

value
Position value.

reportDate
Report date.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.institutional_ownership(symbol="TSLA", cusip="", _from="2022-10-01", to="2022-10-11"))
```

Sample response:
```json
{
"cusip": "023135106",
"data": [
    {
       "ownership": [
         {
            "change": null,
            "cik": "1000097",
            "name": "KINGDON CAPITAL MANAGEMENT, L.L.C.",
           "noVoting": 0,
           "percentage": 6.23893,
           "putCall": "",
           "share": 11250,
           "sharedVoting": 0,
           "soleVoting": 11250,
           "value": 36674000
        }
      ],
      "reportDate": "2022-03-31"
   }
],
"symbol": "AMZN"
}
```

## Insider Transactions (Free)

Python client: `finnhub_client.stock_insider_transactions(...)`

Company insider transactions data sourced from , SEDI and relevant companies' filings. This endpoint covers US, UK, Canada,

Australia, India, and all major EU markets. Limit to 100 transactions per API call.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL. Leave this param blank to get the latest transactions.

from *(optional)*
From date: 2020-03-15.

to *(optional)*
To date: 2020-03-16.

Response Attributes: transaction. A negative value suggests a

data
Array of insider transactions.

change
Number of share changed from the last period. A positive value suggests a
transaction.

filingDate
Filing date.

name
Insider's name.

share
Number of shares held after the transaction.

symbol

Symbol.

transactionCode
Transaction code. A list of codes and their meanings can be found here.

transactionDate
Transaction date.

transactionPrice
Average transaction price.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_insider_transactions('AAPL', '2021-01-01', '2021-03-01'))
```

Sample response:
```json
{
"data": [
    {
       "name": "Kirkhorn Zachary",
       "share": 57234,
       "change": -1250,
       "filingDate": "2021-03-19",
       "transactionDate": "2021-03-17",
       "transactionCode": "S",
      "transactionPrice": 655.81
   },
   {
      "name": "Baglino Andrew D",
      "share": 20614,
      "change": 1000,
      "filingDate": "2021-03-31",
      "transactionDate": "2021-03-29",
      "transactionCode": "M",
      "transactionPrice": 41.57
   },
   {
      "name": "Baglino Andrew D",
      "share": 19114,
      "change": -1500,
      "filingDate": "2021-03-31",
      "transactionDate": "2021-03-29",
      "transactionCode": "S",
      "transactionPrice": 615.75
   }
],
"symbol": "TSLA"
}
```

## Insider Sentiment (Free)

Python client: `finnhub_client.stock_insider_sentiment(...)`

Get insider sentiment data for US companies calculated using method discussed here. The MSPR ranges from -100 for the most negative to
100 for the most positive which can signal price changes in the coming 30-90 days.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

from *(REQUIRED)*
From date: 2020-03-15.

to *(REQUIRED)*
To date: 2020-03-16.

**Response Attributes:**

data
Array of sentiment data.

change
Net buying/selling from all insiders' transactions.

month
Month.

mspr
Monthly share purchase ratio.

symbol
Symbol.

year
Year.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_insider_sentiment('AAPL', '2021-01-01', '2022-03-01'))
```

Sample response:
```json
{
"data":[
    {
       "symbol":"TSLA",
       "year":2021,
       "month":3,
       "change":5540,
       "mspr":12.209097
    },
   {
      "symbol":"TSLA",
      "year":2022,
      "month":1,
      "change":-1250,
      "mspr":-5.6179776
   },
   {
      "symbol":"TSLA",
      "year":2022,
      "month":2,
      "change":-1250,
      "mspr":-2.1459227
   },
   {
      "symbol":"TSLA",
      "year":2022,
      "month":3,
      "change":5870,
      "mspr":8.960191
   }
],
"symbol":"TSLA"
}
```

## Financial Statements (Premium)

Python client: `finnhub_client.financials(...)`

Get standardized balance sheet, income statement and cash flow for global companies going back 30+ years. Data is sourced from original
filings most of which made available through SEC Filings and International Filings endpoints.

Set param to true for faster updates for US companies.

Wondering why our standardized data is different from Bloomberg, Reuters, Factset, S&P or Yahoo Finance ? Check out our FAQ page to learn
more

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

statement REQUIRED for Balance Sheet, Income Statement, Cash Flow respectively.
Statement can take 1 of these values

freq *(REQUIRED)*

Frequency can take 1 of these values . TTM (Trailing Twelve Months) option is available for Income Statement

and Cash Flow. YTD (Year To Date) option is only available for Cash Flow.

preliminary *(optional)*

If set to , it will return Preliminary financial statements for the latest period which are usually available within an hour of the earnings

announcement if finalized data is not available yet. This preliminary data is currently available for US companies. You will see

in the data if that period is using preliminary data.

**Response Attributes:**

financials
An array of map of key, value pairs containing the data for each period.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.financials('AAPL', 'bs', 'annual'))
```

Sample response:
```json
{
"financials": [
         {
            "costOfGoodsSold": 161782,
            "ebit": 63930,
            "grossIncome": 98392,
            "interestExpense": 3576,
            "netIncome": 55256,
            "netIncomeAfterTaxes": 55256,
           "period": "2019-09-28",
           "pretaxIncome": 65737,
           "provisionforIncomeTaxes": 10481,
           "researchDevelopment": 16217,
           "revenue": 260174,
           "sgaExpense": 18245,
           "totalOperatingExpense": 34462,
           "year": 2019
        }
],
"symbol": "AAPL"
}
```

## Financials As Reported (Free)

Python client: `finnhub_client.financials_reported(...)`

Get financials as reported. This data is available for bulk download on Kaggle SEC Financials database.

**Arguments:**

symbol *(optional)*
Symbol.

cik *(optional)*

CIK.

accessNumber *(optional)*
Access number of a specific report you want to retrieve financials from.

freq *(optional)*

Frequency. Can be either or . Default to .

from optional . Filter for endDate.
From date

to optional . Filter for endDate.
To date

Response Attributes: .
.
cik
CIK .

data .
Array of filings.

acceptedDate
Accepted date

accessNumber
Access number.

cik
CIK.

endDate
Period end date

filedDate
Filed date

form
Form type.

quarter
Quarter.

report
Report data.

startDate
Period start date

symbol
Symbol.

year
Year.

symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.financials_reported(symbol='AAPL', freq='annual'))
```

Sample response:
```json
{
"cik": "320193",
"data": [
    {
       "accessNumber": "0000320193-19-000119",
       "symbol": "AAPL",
       "cik": "320193",
       "year": 2019,
       "quarter": 0,
      "form": "10-K",
      "startDate": "2018-09-30 00:00:00",
      "endDate": "2019-09-28 00:00:00",
      "filedDate": "2019-10-31 00:00:00",
      "acceptedDate": "2019-10-30 18:12:36",
      "report": {
         "bs": {
            "Assets": 338516000000,
            "Liabilities": 248028000000,
            "InventoryNet": 4106000000,
            ...
         },
         "cf": {
            "NetIncomeLoss": 55256000000,
            "InterestPaidNet": 3423000000,
            ...
         },
         "ic": {
            "GrossProfit": 98392000000,
            "NetIncomeLoss": 55256000000,
            "OperatingExpenses": 34462000000,
             ...
         }
      }
   }
],
"symbol": "AAPL"
}
```

## Revenue Breakdown (Premium)

Python client: `finnhub_client.stock_revenue_breakdown(...)`

Get revenue breakdown as-reporetd by product and geography. Users on personal plans can access data for US companies which disclose
their revenue breakdown in the annual or quarterly reports.
Global standardized revenue breakdown/segments data is available for Enterprise users. Contact us to inquire about the access for Global
standardized data.
Premium: Premium

**Arguments:**

symbol *(optional)*
Symbol.

cik *(optional)*

CIK.

**Response Attributes:**

cik
CIK
data
Array of revenue breakdown over multiple periods.
accessNumber
Access number of the report from which the data is sourced.
breakdown
Revenue breakdown.
symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_revenue_breakdown('AAPL'))
```

Sample response (truncated):
```json
{
"cik": "320193",
"data": [
    {
       "accessNumber": "0000320193-21-000010",
       "breakdown": {
          "unit": "usd",
          "value": 111439000000,
          "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
         "endDate": "2020-12-26",
         "startDate": "2020-09-27",
         "revenueBreakdown": [
            {
               "axis": "srt:ProductOrServiceAxis",
               "data": [
                {
                    "unit": "usd",
                    "label": "Products",
                    "value": 95678000000,
                    "member": "us-gaap:ProductMember",
                    "percentage": 85.85683647556061
                },
                {
                    "unit": "usd",
                    "label": "Services",
                    "value": 15761000000,
                    "member": "us-gaap:ServiceMember",
                    "percentage": 14.14316352443938
                },
                {
                    "unit": "usd",
                    "label": "Services",
                    "value": 15761000000,
                    "member": "us-gaap:ServiceMember",
                    "percentage": 14.14316352443938
                },
                {
                    "unit": "usd",
                    "label": "iPhone",
                    "value": 65597000000,
...
```

## SEC Filings (Free)

Python client: `finnhub_client.filings(...)`

List company's filing. Limit to 250 documents at a time. This data is available for bulk download on Kaggle SEC Filings database.

Arguments: , and empty to list latest filings.

symbol *(optional)*
Symbol. Leave

cik *(optional)*
CIK.

accessNumber *(optional)*
Access number of a specific report you want to retrieve data from.

form optional to find non-timely filings for a company.
Filter by form. You can use this value

from *(optional)*
From date: 2023-03-15.

to *(optional)*
To date: 2023-03-16.

Response Attributes: .
.
acceptedDate
Accepted date

accessNumber
Access number.

cik
CIK.

filedDate
Filed date

filingUrl
Filing's URL.

form
Form type.

reportUrl
Report's URL.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.filings(symbol='AAPL', _from="2020-01-01", to="2020-06-11"))
```

Sample response:
```json
[
{
    "accessNumber": "0001193125-20-050884",
    "symbol": "AAPL",
    "cik": "320193",
    "form": "8-K",
    "filedDate": "2020-02-27 00:00:00",
    "acceptedDate": "2020-02-27 06:14:21",
    "reportUrl": "https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000119312520050884/d865740d8k.htm",
   "filingUrl": "https://www.sec.gov/Archives/edgar/data/320193/000119312520050884/0001193125-20-050884-index.html"
},
{
   "accessNumber": "0001193125-20-039203",
   "symbol": "AAPL",
   "cik": "320193",
   "form": "8-K",
   "filedDate": "2020-02-18 00:00:00",
   "acceptedDate": "2020-02-18 06:24:57",
   "reportUrl": "https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000119312520039203/d845033d8k.htm",
   "filingUrl": "https://www.sec.gov/Archives/edgar/data/320193/000119312520039203/0001193125-20-039203-index.html"
},
...
]
```

## SEC Sentiment Analysis (Premium)

Python client: `finnhub_client.sec_sentiment_analysis(...)`

Get sentiment analysis of 10-K and 10-Q filings from SEC. An abnormal increase in the number of positive/negative words in filings can signal
a significant change in the company's stock price in the upcoming 4 quarters. We make use of Loughran and McDonald Sentiment Word Lists
to calculate the sentiment for each filing.

**Arguments:**

accessNumber *(REQUIRED)*
Access number of a specific report you want to retrieve data from.

**Response Attributes:**

accessNumber
Access number.

cik
CIK.

sentiment
Filing Sentiment

constraining
% of constraining words in the filing.

litigious

% of litigious words in the filing.

modal-moderate
% of modal-moderate words in the filing.

modal-strong
% of modal-strong words in the filing.

modal-weak
% of modal-weak words in the filing.

negative
% of negative words in the filing.

polarity
% of polarity words in the filing.

positive
% of positive words in the filing.

uncertainty
% of uncertainty words in the filing.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.sec_sentiment_analysis('0000320193-20-000052'))
```

Sample response:
```json
{
"cik": "320193",
"symbol": "AAPL",
"accessNumber": "0000320193-20-000052",
"sentiment": {
    "negative": 1.2698412698412698,
    "polarity": -0.1147540479911535,
    "positive": 0.5042016806722689,
    "litigious": 0.2427637721755369,
   "modal-weak": 0.392156862745098,
   "uncertainty": 1.1391223155929038,
   "constraining": 0.5975723622782446,
   "modal-strong": 0.14939309056956115,
   "modal-moderate": 0.11204481792717086
}
}
```

## Similarity Index (Premium)

Python client: `finnhub_client.sec_similarity_index(...)`

Calculate the textual difference between a company's 10-K / 10-Q reports and the same type of report in the previous year using Cosine
Similarity. For example, this endpoint compares 2019's 10-K with 2018's 10-K. Companies breaking from its routines in disclosure of financial
condition and risk analysis section can signal a significant change in the company's stock price in the upcoming 4 quarters.

**Arguments:**

symbol *(optional)*
Symbol. Required if cik is empty

cik *(optional)*
CIK. Required if symbol is empty

freq optional . Default to
or

**Response Attributes:**

cik
CIK.

similarity
Array of filings with its cosine similarity compared to the same report of the previous year.

acceptedDate

Accepted date .

accessNumber
Access number.

cik
CIK.

filedDate

Filed date .

filingUrl
Filing's URL.

form
Form type.

item1
Cosine similarity of Item 1 (Business). This number is only available for Annual reports.

item1a
Cosine similarity of Item 1A (Risk Factors). This number is available for both Annual and Quarterly reports.

item2
Cosine similarity of Item 2 (Management's Discussion and Analysis of Financial Condition and Results of Operations). This number is
only available for Quarterly reports.

item7
Cosine similarity of Item 7 (Management's Discussion and Analysis of Financial Condition and Results of Operations). This number is
only available for Annual reports.

item7a
Cosine similarity of Item 7A (Quantitative and Qualitative Disclosures About Market Risk). This number is only available for Annual
reports.

reportUrl
Report's URL.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.sec_similarity_index('AAPL'))
```

Sample response:
```json
{
"cik": "320193",
"similarity": [
    {
       "cik": "320193",
       "accessNumber": "0000320193-19-000119",
       "item1": 0.8833750347608914,
       "item2": 0,
       "item1a": 0.994836154829746,
      "item7": 0.897030072745,
      "item7a": 0.9843052590436008,
      "form": "10-K",
      "reportUrl": "https://www.sec.gov/ix?doc=/Archives/edgar/data/320193/000032019319000119/a10-k20199282019.htm",
      "filingUrl": "https://www.sec.gov/Archives/edgar/data/320193/000032019319000119/0000320193-19-000119-index.html",
      "filedDate": "2019-10-31 00:00:00",
      "acceptedDate": "2019-10-30 18:12:36"
   },
   {
      "cik": "320193",
      "accessNumber": "0000320193-18-000145",
      "item1": 0.9737784696339462,
      "item2": 0,
      "item1a": 0.9931651573630014,
      "item7": 0.9441063774798184,
      "item7a": 0.9856181212005336,
      "form": "10-K",
      "reportUrl": "https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/a10-k20189292018.htm",
      "filingUrl": "https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/0000320193-18-000145-index.html",
      "filedDate": "2018-11-05 00:00:00",
      "acceptedDate": "2018-11-05 08:01:40"
   }
],
"symbol": "AAPL"
}
```

## IPO Calendar (Free)

Python client: `finnhub_client.ipo_calendar(...)`

Get recent and upcoming IPO.

**Arguments:**

from *(REQUIRED)*
From date: 2020-03-15.
to *(REQUIRED)*
To date: 2020-03-16.

**Response Attributes:**

ipoCalendar
Array of IPO events.

date

IPO date.

exchange
Exchange.

name
Company's name.

numberOfShares
Number of shares offered during the IPO.

price
Projected price or price range.

status

IPO status. Can take 1 of the following values: , , ,

symbol
Symbol.

totalSharesValue
Total shares value.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.ipo_calendar(_from="2020-05-01", to="2020-06-01"))
```

Sample response:
```json
{
"ipoCalendar": [
    {
       "date": "2020-04-03",
       "exchange": "NASDAQ Global",
       "name": "ZENTALIS PHARMACEUTICALS, LLC",
       "numberOfShares": 7650000,
       "price": "16.00-18.00",
       "status": "expected",
      "symbol": "ZNTL",
      "totalSharesValue": 158355000
   },
   {
      "date": "2020-04-01",
      "exchange": "NASDAQ Global",
      "name": "WIMI HOLOGRAM CLOUD INC.",
      "numberOfShares": 5000000,
      "price": "5.50-7.50",
      "status": "expected",
      "symbol": "WIMI",
      "totalSharesValue": 43125000
   },
]
}
```

## Dividends (Premium)

Python client: `finnhub_client.stock_dividends(...)`

Get dividends data for common stocks going back 30 years.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

from *(REQUIRED)*
YYYY-MM-DD.

to *(REQUIRED)*
YYYY-MM-DD.

**Response Attributes:**

adjustedAmount
Adjusted dividend.
amount
Amount in local currency.
currency
Currency.
date
Ex-Dividend date.
declarationDate
Declaration date.
freq
Dividend frequency. Can be 1 of the following values:

payDate
Pay date.
recordDate
Record date.
symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_dividends('KO', _from='2019-01-01', to='2020-01-01'))
```

Sample response (truncated):
```json
[
{
              "symbol": "AAPL",
              "date": "2019-11-07",
              "amount": 0.77,
              "adjustedAmount": 0.77,
              "payDate": "2019-11-14",
              "recordDate": "2019-11-11",
              "declarationDate": "2019-10-30",
             "currency": "USD"
},
{
             "symbol": "AAPL",
             "date": "2019-08-09",
             "amount": 0.77,
             "adjustedAmount": 0.77,
             "payDate": "2019-08-15",
             "recordDate": "2019-08-12",
             "declarationDate": "2019-07-30",
             "currency": "USD"
},
{
             "symbol": "AAPL",
             "date": "2019-05-10",
             "amount": 0.77,
             "adjustedAmount": 0.77,
             "payDate": "2019-05-16",
             "recordDate": "2019-05-13",
             "declarationDate": "2019-05-01",
             "currency": "USD"
},
{
             "symbol": "AAPL",
             "date": "2019-02-08",
             "amount": 0.73,
             "adjustedAmount": 0.77,
             "payDate": "2019-02-14",
             "recordDate": "2019-02-11",
             "declarationDate": "2019-01-29",
...
```

## Sector Metrics (Premium)

Python client: `finnhub_client.sector_metric(...)`

Get ratios for different sectors and regions/indices.

**Arguments:**

region *(REQUIRED)*
Region. A list of supported values for this field can be found here.

**Response Attributes:**

data
Metrics for each sector.
metrics
Metrics data in key-value format. and fields are for average and median respectively.

sector

Sector

region
Region.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.sector_metric('NA'))
```

Sample response:
```json
{
"data": [
    {
           "metrics": {
            "assetTurnoverAnnual": {
               "a": 0.7245,
               "m": 0.5426
            },
            "assetTurnoverTTM": {
              "a": 0.7254,
              "m": 0.5463
           },
          },
          "sector": "Communication Services"
   },
   {
          "metrics": {
           "currentDividendYieldTTM": {
              "a": 30.9763,
              "m": 2.09
           },
           "currentEv/freeCashFlowAnnual": {
              "a": 286.4793,
              "m": 19.8488
           },
          },
          "sector": "Consumer Discretionary"
   }
],
"region": "Asia_Ocenia"
}
```

## Price Metrics (Premium)

Python client: `finnhub_client.price_metrics(...)`

Get company price performance statistics such as 52-week high/low, YTD return and much more.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

**Response Attributes:**

atDate

Data date.

data
Map key-value pair of key ratios and metrics.

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.price_metrics('AAPL'))
```

Sample response:
```json
{
"data": {
       "100DayEMA": 295.7694,
       "100DaySMA": 319.2297,
       "10DayAverageTradingVolume": 53717320,
       "10DayEMA": 247.4641,
       "10DaySMA": 247.372,
       "14DayRSI": 34.0517,
       "1MonthHigh": 314.67,
      "1MonthHighDate": "2022-08-16",
      "50DayEMA": 277.482,
      "50DaySMA": 288.313,
      "52WeekHigh": 414.5,
      "52WeekHighDate": "2021-11-04",
      "52WeekLow": 206.86,
      "52WeekLowDate": "2022-05-24",
      "5DayEMA": 245.8814,
      "ytdPriceReturn": 10.1819
},
"symbol": "TSLA"
}
```

## Symbol Change (Premium)

Python client: `finnhub_client.symbol_change(...)`

Get a list of symbol changes for US-listed, EU-listed, NSE and ASX securities. Limit to 2000 events at a time.

**Arguments:**

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data

Array of symbol change events.

atDate
Event's date.

newSymbol
New symbol.

oldSymbol
Old symbol.

fromDate
From date.

toDate
To date.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.symbol_change(_from="2022-10-01", to="2022-10-11"))
```

Sample response:
```json
{
"data": [
       {
          "atDate": "2022-10-05",
          "newSymbol": "MEN.L",
          "oldSymbol": "PPC.L"
       }
],
"fromDate": "2022-10-01",
"toDate": "2022-10-30"
}
```

## ISIN Change (Premium)

Python client: `finnhub_client.isin_change(...)`

Get a list of ISIN changes for EU-listed securities. Limit to 2000 events at a time.

**Arguments:**

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data
Array of ISIN change events.

atDate

Event's date.

newIsin
New ISIN.

oldIsin
Old ISIN.

fromDate
From date.

toDate
To date.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.isin_change(_from="2022-10-01", to="2022-10-11"))
```

Sample response:
```json
{
"data": [
       {
           "atDate": "2021-08-30",
           "newIsin": "DE000A3E5CP0",
           "oldIsin": "DE0007239402"
       }
],
"fromDate": "2021-08-07",
"toDate": "2021-10-07"
}
```

## Historical Market Cap (Premium)

Python client: `finnhub_client.historical_market_cap(...)`

Get historical market cap data for global companies.
Premium: Accessible with Fundamental 2 or All in One subscription.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

currency

Currency

data
Array of market data.

atDate
Date of the reading

marketCapitalization
Value

symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.historical_market_cap('AAPL', _from="2020-06-01", to="2020-06-10"))
```

Sample response:
```json
{
"currency": "USD",
"data": [
       {
          "atDate": "2024-06-10",
          "marketCapitalization": 3759.182
       },
       {
          "atDate": "2024-06-09",
         "marketCapitalization": 21508.447
      }
],
"symbol": "SYM"
}
```

## Historical Employee Count (Premium)

Python client: `finnhub_client.historical_employee_count(...)`

Get historical employee count for global companies.

Premium: Accessible with Fundamental 2 or All in One subscription.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data

Array of market data.

atDate
Date of the reading

employee
Value

symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.historical_employee_count('AAPL', _from="2020-06-01", to="2020-06-10"))
```

Sample response:
```json
{
"data": [
        {
           "atDate": "2023-09-30",
           "employee": 161000
        },
        {
           "atDate": "2022-09-24",
           "employee": 164000
       },
       {
          "atDate": "2021-09-25",
          "employee": 154000
       },
       {
          "atDate": "2020-09-26",
          "employee": 147000
       }
],
"symbol": "AAPL"
}
```

## Recommendation Trends (Free)

Python client: `finnhub_client.recommendation_trends(...)`

Get latest analyst recommendation trends for a company.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

**Response Attributes:**

buy
Number of recommendations that fall into the Buy category

hold

Number of recommendations that fall into the Hold category

period
Updated period

sell
Number of recommendations that fall into the Sell category

strongBuy
Number of recommendations that fall into the Strong Buy category

strongSell
Number of recommendations that fall into the Strong Sell category

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.recommendation_trends('AAPL'))
```

Sample response:
```json
[
{
       "buy": 24,
       "hold": 7,
       "period": "2025-03-01",
       "sell": 0,
       "strongBuy": 13,
       "strongSell": 0,
       "symbol": "AAPL"
},
{
      "buy": 17,
      "hold": 13,
      "period": "2025-02-01",
      "sell": 5,
      "strongBuy": 13,
      "strongSell": 0,
      "symbol": "AAPL"
}
]
Widget:
AAPL Recommendation Trends

# Analysts

                          Jun 2026       Jul 2026  Aug 2026              Sep 2026                                 Oct 2026
May 2026  Strong Buy                    Sell      Strong Sell
Buy  Hold
```

## Price Target (Premium)

Python client: `finnhub_client.price_target(...)`

Get latest price target consensus.
Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

**Response Attributes:**

lastUpdated
Updated time of the data
numberAnalysts
Number of Analysts.
symbol
Company symbol.
targetHigh
Highes analysts' target.
targetLow
Lowest analysts' target.
targetMean
Mean of all analysts' targets.
targetMedian
Median of all analysts' targets.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.price_target('AAPL'))
```

Sample response:
```json
{
"lastUpdated": "2023-04-06 00:00:00",
"numberAnalysts": 39,
"symbol": "NFLX",
"targetHigh": 462,
"targetLow": 217.15,
"targetMean": 364.37,
"targetMedian": 359.04
}
Widget:
NVDA Stock Price Target
PAST 12 MONTHS WITH 12 MONTHS FORECAST
Stock Price                                                                                                                                   $600
$500
$400
$300
$200
$100
Jan 2026           Jul 2026                                                                                  Jan 2027  Jul 2027
Monthly values are snapshots, not daily price paths. Price targets are analysts' estimates, not guarantees.
```

## Stock Upgrade/Downgrade (Premium)

Python client: `finnhub_client.upgrade_downgrade(...)`

Get latest stock upgrade and downgrade.

**Arguments:**

symbol *(optional)*
Symbol of the company: AAPL. If left blank, the API will return latest stock upgrades/downgrades.

from *(optional)*
From date: 2000-03-15.

to *(optional)*
To date: 2020-03-16.

.

**Response Attributes:**

action
Action can take any of the following values:

company
Company/analyst who did the upgrade/downgrade.

fromGrade
From grade.

gradeTime
Upgrade/downgrade time in UNIX timestamp.

symbol
Company symbol.

toGrade
To grade.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.upgrade_downgrade(symbol='AAPL', _from='2020-01-01', to='2020-06-30'))
```

Sample response:
```json
[
{
    "symbol": "BYND",
    "gradeTime": 1567728000,
    "company": "DA Davidson",
    "fromGrade": "",
    "toGrade": "Underperform",
    "action": "init"
},
{
   "symbol": "BYND",
   "gradeTime": 1566259200,
   "company": "JP Morgan",
   "fromGrade": "Neutral",
   "toGrade": "Overweight",
   "action": "up"
},
{
   "symbol": "BYND",
   "gradeTime": 1564704000,
   "company": "Bank of America",
   "fromGrade": "",
   "toGrade": "Neutral",
   "action": "reit"
}
]
```

## Revenue Estimates (Premium)

Python client: `finnhub_client.company_revenue_estimates(...)`

Get company's revenue estimates.

. Default to

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

numberAnalysts
Number of Analysts.

period
Period.

quarter
Fiscal quarter.

revenueAvg
Average revenue estimates including Finnhub's proprietary estimates.

revenueHigh
Highest estimate.

revenueLow
Lowest estimate.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_revenue_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "revenueAvg": 58800500000,
       "revenueHigh": 64060000000,
       "revenueLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "revenueAvg": 61287300000,
      "revenueHigh": 66557000000,
      "revenueLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Earnings Estimates (Premium)

Python client: `finnhub_client.company_eps_estimates(...)`

Get company's EPS estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

epsAvg
Average EPS estimates including Finnhub's proprietary estimates.

epsHigh
Highest estimate.

epsLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter

Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_eps_estimates('AAPL', freq='quarterly'))
```

Sample response:
```json
{
"data": [
       {
          "epsAvg": 2.65,
          "epsHigh": 2.98,
          "epsLow": 2.05,
          "numberAnalysts": 35,
          "period": "2020-06-30",
          "quarter": 3,
         "year": 2020
      },
      {
         "epsAvg": 2.52,
         "epsHigh": 3.02,
         "epsLow": 2.21,
         "numberAnalysts": 34,
         "period": "2020-03-31",
         "quarter": 2,
         "year": 2020
      }
],
"freq": "quarterly",
"symbol": "AAPL"
}
Widget:
AAPL - EPS Estimates
EPS High    EPS Average              EPS Low

Quarterly EPS Estimates  3

                         12-31       03-31        06-30       09-30       12-31
-30   026-        027-         027-        027-        027-
          2            2           2           2
-

```

## EBITDA Estimates (Premium)

Python client: `finnhub_client.company_ebitda_estimates(...)`

Get company's ebitda estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

ebitdaAvg
Average EBITDA estimates including Finnhub's proprietary estimates.

ebitdaHigh
Highest estimate.

ebitdaLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_ebitda_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "ebitdaAvg": 58800500000,
       "ebitdaHigh": 64060000000,
       "ebitdaLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "ebitdaAvg": 61287300000,
      "ebitdaHigh": 66557000000,
      "ebitdaLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## EBIT Estimates (Premium)

Python client: `finnhub_client.company_ebit_estimates(...)`

Get company's ebit estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

ebitAvg
Average EBIT estimates including Finnhub's proprietary estimates.

ebitHigh
Highest estimate.

ebitLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter

Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_ebit_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "ebitAvg": 58800500000,
       "ebitHigh": 64060000000,
       "ebitLow": 54072000000
       "quarter": 3,
      "year": 2020,
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "ebitAvg": 61287300000,
      "ebitHigh": 66557000000,
      "ebitLow": 54871000000,
      "quarter": 2,
      "year": 2020,
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Net Income Estimates (Premium)

Python client: `finnhub_client.company_net_income_estimates(...)`

Get company's net income estimates.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*

Can take 1 of the following values: . Default to

**Response Attributes:**

data
List of estimates

netIncomeAvg
Average net income estimates including Finnhub's proprietary estimates.

netIncomeHigh
Highest estimate.

netIncomeLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_net_income_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "netIncomeAvg": 58800500000,
       "netIncomeHigh": 64060000000,
       "netIncomeLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "netIncomeAvg": 61287300000,
      "netIncomeHigh": 66557000000,
      "netIncomeLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Pretax Income Estimates (Premium)

Python client: `finnhub_client.company_pretax_income_estimates(...)`

Get company's pretax income estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

numberAnalysts
Number of Analysts.

period
Period.

pretaxIncomeAvg
Average pretax income estimates including Finnhub's proprietary estimates.

pretaxIncomeHigh
Highest estimate.

pretaxIncomeLow
Lowest estimate.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_pretax_income_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "pretaxIncomeAvg": 58800500000,
       "pretaxIncomeHigh": 64060000000,
       "pretaxIncomeLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "pretaxIncomeAvg": 61287300000,
      "pretaxIncomeHigh": 66557000000,
      "pretaxIncomeLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Gross Income Estimates (Premium)

Python client: `finnhub_client.company_gross_income_estimates(...)`

Get company's gross income estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

grossIncomeAvg
Average gross income estimates including Finnhub's proprietary estimates.

grossIncomeHigh
Highest estimate.

grossIncomeLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period

Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_gross_income_estimates('TSLA', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "grossIncomeAvg": 58800500000,
       "grossIncomeHigh": 64060000000,
       "grossIncomeLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "grossIncomeAvg": 61287300000,
      "grossIncomeHigh": 66557000000,
      "grossIncomeLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## DPS Estimates (Premium)

Python client: `finnhub_client.company_dps_estimates(...)`

Get company's Dividend per Share estimates.

**Arguments:**

symbol REQUIRED . Default to

Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

dpsAvg
Average DPS estimates including Finnhub's proprietary estimates.

dpsHigh
Highest estimate.

dpsLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_dps_estimates('AAPL', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "dpsAvg": 0.82,
       "dpsHigh": 0.9,
       "dpsLow": 0.74,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "dpsAvg": 0.77,
      "dpsHigh": 0.88,
      "dpsLow": 0.7,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## FCF Estimates (Premium)

Python client: `finnhub_client.company_fcf_estimates(...)`

Get company's free cash flow estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

fcfAvg
Average FCF estimates including Finnhub's proprietary estimates.

fcfHigh
Highest estimate.

fcfLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter

Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_fcf_estimates('AAPL', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "fcfAvg": 58800500000,
       "fcfHigh": 64060000000,
       "fcfLow": 54072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "fcfAvg": 61287300000,
      "fcfHigh": 66557000000,
      "fcfLow": 54871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Capex Estimates (Premium)

Python client: `finnhub_client.company_capex_estimates(...)`

Get company's capital expenditure estimates.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*

Can take 1 of the following values: . Default to

**Response Attributes:**

data
List of estimates

capexAvg
Average capex estimates including Finnhub's proprietary estimates.

capexHigh
Highest estimate.

capexLow
Lowest estimate.

numberAnalysts
Number of Analysts.

period
Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_capex_estimates('AAPL', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "capexAvg": 2800000000,
       "capexHigh": 3200000000,
       "capexLow": 2400000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "capexAvg": 2600000000,
      "capexHigh": 3000000000,
      "capexLow": 2200000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## OCF Estimates (Premium)

Python client: `finnhub_client.company_ocf_estimates(...)`

Get company's operating cash flow estimates.

Arguments: . Default to

symbol *(REQUIRED)*
Symbol of the company: AAPL.

freq *(optional)*
Can take 1 of the following values:

**Response Attributes:**

data
List of estimates

numberAnalysts
Number of Analysts.

ocfAvg
Average OCF estimates including Finnhub's proprietary estimates.

ocfHigh
Highest estimate.

ocfLow
Lowest estimate.

period
Period.

quarter
Fiscal quarter.

year
Fiscal year.

freq
Frequency: annual or quarterly.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_ocf_estimates('AAPL', freq='quarterly'))
```

Sample response:
```json
{
"data": [
    {
       "numberAnalysts": 31,
       "period": "2020-06-30",
       "ocfAvg": 68800500000,
       "ocfHigh": 74060000000,
       "ocfLow": 64072000000,
       "quarter": 3,
      "year": 2020
   },
   {
      "numberAnalysts": 31,
      "period": "2020-03-31",
      "ocfAvg": 71287300000,
      "ocfHigh": 76557000000,
      "ocfLow": 64871000000,
      "quarter": 2,
      "year": 2020
   }
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## Earnings Surprises (Free)

Python client: `finnhub_client.company_earnings(...)`

Get company historical quarterly earnings surprise going back to 2000.
Free Tier: Last 4 quarters

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

limit *(optional)*
Limit number of period returned. Leave blank to get the full history.

**Response Attributes:**

actual
Actual earning result.
estimate
Estimated earning.
period
Reported period.
quarter
Fiscal quarter.
surprise
Surprise - The difference between actual and estimate.

surprisePercent

Surprise percent.

symbol
Company symbol.

year
Fiscal year.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_earnings('TSLA', limit=5))
```

Sample response:
```json
[
{
       "actual": 1.88,
       "estimate": 1.9744,
       "period": "2023-03-31",
       "quarter": 1,
       "surprise": -0.0944,
       "surprisePercent": -4.7812,
       "symbol": "AAPL",
      "year": 2023
},
{
      "actual": 1.29,
      "estimate": 1.2957,
      "period": "2022-12-31",
      "quarter": 4,
      "surprise": -0.0057,
      "surprisePercent": -0.4399,
      "symbol": "AAPL",
      "year": 2022
},
{
      "actual": 1.2,
      "estimate": 1.1855,
      "period": "2022-09-30",
      "quarter": 3,
      "surprise": 0.0145,
      "surprisePercent": 1.2231,
      "symbol": "AAPL",
      "year": 2022
}
]
Widget:
AAPL - Historical EPS Surprises
Actual  Estimate

Quarterly EPS  2
                         2025-09-30            2025-12-31  2026-03-31  2026-06-30
-06-30   Beat: 0.04            Beat: 0.11  Beat: 0.02  Missed: 0.02
Beat: 0.11
```

## Earnings Calendar (Free)

Python client: `finnhub_client.earnings_calendar(...)`

Get historical and coming earnings release. EPS and Revenue in this endpoint are non-GAAP, which means they are adjusted to exclude some
one-time or unusual items. This is the same data investors usually react to and talked about on the media. Estimates are sourced from both
sell-side and buy-side analysts.

Free Tier: 1 month of historical earnings and new updates

**Arguments:**

from *(optional)*
From date: 2020-03-15.

to *(optional)*
To date: 2020-03-16.

symbol *(optional)*
Filter by symbol: AAPL.

international *(optional)*

Set to to include international markets. Default value is

**Response Attributes:**

earningsCalendar
Array of earnings release.

date
Date.

epsActual
EPS actual.

epsEstimate
EPS estimate.

hour

Indicates whether the earnings is announced before market open( ), after market close( ), or during market hour( ).

quarter
Earnings quarter.

revenueActual
Revenue actual.

revenueEstimate
Revenue estimate including Finnhub's proprietary estimates.

symbol
Symbol.

year
Earnings year.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.earnings_calendar(_from="2021-06-10", to="2021-06-30", symbol="", international=False))
```

Sample response:
```json
{
"earningsCalendar": [
    {
       "date": "2020-01-28",
       "epsActual": 4.99,
       "epsEstimate": 4.5474,
       "hour": "amc",
       "quarter": 1,
       "revenueActual": 91819000000,
      "revenueEstimate": 88496400810,
      "symbol": "AAPL",
      "year": 2020
   },
   {
      "date": "2019-10-30",
      "epsActual": 3.03,
      "epsEstimate": 2.8393,
      "hour": "amc",
      "quarter": 4,
      "revenueActual": 64040000000,
      "revenueEstimate": 62985161760,
      "symbol": "AAPL",
      "year": 2019
   }
]
}
```

## Quote (Free)

Python client: `finnhub_client.quote(...)`

Get real-time quote data for US stocks. Constant polling is not recommended. Use websocket if you need real-time updates.
Real-time stock prices for international markets are supported for Enterprise clients via our partner's feed. Contact Us to learn more.

**Arguments:**

symbol *(REQUIRED)*
Symbol

**Response Attributes:**

c
Current price

d
Change

dp
Percent change

h
High price of the day

l
Low price of the day

o
Open price of the day

pc
Previous close price

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.quote('AAPL'))
```

Sample response:
```json
{
"c": 261.74,
"h": 263.31,
"l": 260.68,
"o": 261.07,
"pc": 259.45,
"t": 1582641000
}
```

## Stock Candles (Premium)

Python client: `finnhub_client.stock_candles(...)`

Get candlestick data (OHLCV) for stocks.
Daily data will be adjusted for Splits. Intraday data will remain unadjusted. Only 1 month of intraday will be returned at a time. If you need
more historical intraday data, please use the from and to params iteratively to request more data.

Arguments: .Some timeframes might not be available depending on the exchange.

symbol *(REQUIRED)*
Symbol.

resolution *(REQUIRED)*
Supported resolution includes

from *(REQUIRED)*
UNIX timestamp. Interval initial value.

to *(REQUIRED)*
UNIX timestamp. Interval end value.

**Response Attributes:**

c
List of close prices for returned candles.

h
List of high prices for returned candles.

l
List of low prices for returned candles.

o
List of open prices for returned candles.

s
Status of the response. This field can either be ok or no_data.

t
List of timestamp for returned candles.

v
List of volume data for returned candles.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249))
```

Sample response:
```json
{
"c": [
       217.68,
       221.03,
       219.89
],
"h": [
       222.49,
       221.5,
      220.94
],
"l": [
      217.19,
      217.1402,
      218.83
],
"o": [
      221.03,
      218.55,
      220
],
"s": "ok",
"t": [
      1569297600,
      1569384000,
      1569470400
],
"v": [
      33463820,
      24018876,
      20730608
]
}
Widget:
Tick Data Premium
Get historical tick data for global exchanges.
For more historical tick data, you can visit our bulk download page in the Dashboard here to speed up the download process.
Exchange              Segment                                                             Delay
US CTA/UTP            Full SIP                                                            End-of-day
```

## Delay (Free)

Python client: `finnhub_client.stock_tick(...)`

Exchange Segment End-of-day
15 minute
TSX TSX End-of-day
LSE TSX Venture
Euronext Index End-of-day

Deutsche B�rse London Stock Exchange (L)
LSE International (L)
Method: LSE European (L)
Examples: Euronext Paris (PA)
Euronext Amsterdam (AS)
Euronext Lisbon (LS)
Euronext Brussels (BR)
Euronext Oslo (OL)
Euronext London (LN)
Euronext Dublin (IR)
Index
Warrant

Frankfurt (F)
Xetra (DE)
Duesseldorf (DU)
Hamburg (HM)
Berlin (BE)
Hanover (HA)
Stoxx (SX)
TradeGate (TG)
Zertifikate (SC)
Index
Warrant

**Arguments:**

symbol *(REQUIRED)*
Symbol.

date *(REQUIRED)*
Date: 2020-04-02.

limit *(REQUIRED)*
Limit number of ticks returned. Maximum value:

skip *(REQUIRED)*
Number of ticks to skip. Use this parameter to loop through the entire data.

**Response Attributes:**

c
List of trade conditions. A comprehensive list of trade conditions code can be found here

count < , all data for that date has been returned.
Number of ticks returned. If

p

List of price data.

s
Symbol.

skip
Number of ticks skipped.

t
List of timestamp in UNIX ms.

total
Total number of ticks for that date.

v
List of volume data.

x
List of venues/exchanges. A list of exchange codes can be found here

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_tick('AAPL', '2020-03-25', 500, 0))
```

Sample response:
```json
{
"p": [
    255,
    255,
    255
],
"s": "AAPL",
"skip": 0,
"t": [
   1585108800073,
   1585108800315,
   1585108800381
],
"v": [
   2513,
   24,
   1
],
"x": [
   "P",
   "P",
   "P"
],
"count": 3,
"c":[["1","24"],["1","24","12"],["1","24","12"]]
}
```

## Historical NBBO (Premium)

Python client: `finnhub_client.stock_nbbo(...)`

Get historical best bid and offer for US stocks, LSE, TSX, Euronext and Deutsche Borse.

For US market, this endpoint only serves historical NBBO from the beginning of 2026. To download more historical data, please visit our bulk
download page in the Dashboard here.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

date *(REQUIRED)*
Date: 2020-04-02.

limit *(REQUIRED)*
Limit number of ticks returned. Maximum value:

skip *(REQUIRED)*
Number of ticks to skip. Use this parameter to loop through the entire data.

**Response Attributes:**

a
List of Ask price data.

av
List of Ask volume data.

ax
List of venues/exchanges - Ask price. A list of exchange codes can be found here

b
List of Bid price data.

bv
List of Bid volume data.

bx
List of venues/exchanges - Bid price. A list of exchange codes can be found here

c
List of quote conditions. A comprehensive list of quote conditions code can be found here

count < , all data for that date has been returned.
Number of ticks returned. If

s
Symbol.

skip
Number of ticks skipped.

t
List of timestamp in UNIX ms.

total
Total number of ticks for that date.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_nbbo('AAPL', '2020-03-25', 500, 0))
```

Sample response (truncated):
```json
{
"a": [
    137,
    133.2,
    126.08
],
"av": [
    1,
    2,
   1
],
"ax": [
   "P",
   "P",
   "P"
],
"b": [
   116.5,
   116.5,
   116.5
],
"bv": [
   1,
   1,
   1
],
"bx": [
   "P",
   "P",
   "P"
],
"c": [
   [
      "1"
   ],
   [
      "1"
   ],
   [
      "1"
...
```

## Last Bid-Ask (Premium)

Python client: `finnhub_client.last_bid_ask(...)`

Get last bid/ask data for US stocks.

**Arguments:**

symbol *(REQUIRED)*

Symbol.

**Response Attributes:**

a
Ask price.
av
Ask volume.
b
Bid price.
bv
Bid volume.
t
Reference UNIX timestamp in ms.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.last_bid_ask('AAPL'))
```

Sample response:
```json
{
"a": 338.65,
"av": 2,
"b": 338.61,
"bv": 2,
"t": 1591995678874
}
```

## Splits (Premium)

Python client: `finnhub_client.stock_splits(...)`

Get splits data for stocks.
Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

from *(REQUIRED)*
YYYY-MM-DD.

to *(REQUIRED)*
YYYY-MM-DD.

**Response Attributes:**

date
Split date.

fromFactor
From factor.

symbol
Symbol.

toFactor
To factor.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_splits('AAPL', _from='2000-01-01', to='2020-01-01'))
```

Sample response:
```json
[
{
  "symbol": "AAPL",
  "date": "2014-06-09",
  "fromFactor": 1,
  "toFactor": 7
}
]
```

## Dividends 2 (Basic) (Premium)

Python client: `finnhub_client.stock_basic_dividends(...)`

Get global dividends data.

Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

data

amount
Amount in local currency.

exDate
Ex-Dividend date.

symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_basic_dividends('AAPL'))
```

Sample response:
```json
{
"data": [
{
     "exDate": "2019-11-07",
     "amount": 0.77,

},
{
     "exDate": "2019-08-09",
    "amount": 0.77,
},
{
    "exDate": "2019-05-10",
    "amount": 0.77,
}
],
"symbol": "AAPL"
}
```

## Indices Constituents (Premium)

Python client: `finnhub_client.indices_const(...)`

Get a list of index's constituents. A list of supported indices for this endpoint can be found here.

**Arguments:**

symbol *(REQUIRED)*
symbol

**Response Attributes:**

constituents
Array of constituents.
constituentsBreakdown
Array of constituents' details.
cusip
Cusip.
isin
ISIN.
name
Name.
shareClassFIGI

Global Share Class FIGI.

symbol
Symbol.

weight
Weight.

symbol
Index's symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.indices_const(symbol = "^IBEX"))
```

Sample response:
```json
{
"atDate": "2026-07-24",
"constituents": [
    "SAN.MC",
    "IBE.MC",
],
"constituentsBreakdown": [
    {
       "cusip": "E19790109",
      "isin": "ES0113900J37",
      "name": "Banco Santander SA",
      "shareClassFIGI": "BBG001S6GQ80",
      "symbol": "SAN.MC",
      "weight": 17.53587
   },
   {
      "cusip": "E6165F166",
      "isin": "ES0144580Y14",
      "name": "Iberdrola SA",
      "shareClassFIGI": "BBG001S68N31",
      "symbol": "IBE.MC",
      "weight": 14.28294
   }
],
"symbol": "^IBEX"
}
```

## ETFs Profile (Premium)

Python client: `finnhub_client.etfs_profile(...)`

Get ETF profile information. This endpoint has global coverage. A list of supported ETFs can be found here.
Premium: Premium required.

**Arguments:**

symbol *(optional)*
ETF symbol.

isin *(optional)*

ETF isin.

**Response Attributes:**

profile
Profile data.

assetClass
Asset Class.

aum
AUM.

avgVolume
30-day average volume.

cusip
CUSIP.

description
ETF's description.

dividendYield
Dividend yield.

domicile
ETF domicile.

etfCompany
ETF issuer.

expenseRatio
Expense ratio. For non-US funds, this is the KID ongoing charges.

inceptionDate
Inception date.

investmentSegment
Investment Segment.

isInverse
Whether the ETF is inverse

isLeveraged
Whether the ETF is leveraged

isin
ISIN.

leverageFactor
Leverage factor.

logo
Logo.

name
Name

nav
NAV.

navCurrency
NAV currency.

priceToBook
P/B.

priceToEarnings

P/E.

trackingIndex
Tracking Index.

website
ETF's website.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.etfs_profile('SPY'))
```

Sample response:
```json
{
"profile": {
  "assetClass": "Equity",
  "aum": 318374000000,
  "avgVolume": 63794600,
  "cusip": "",
  "description": "SPY was created on 1993-01-22 by SPDR. The fund's investment portfolio concentrates primarily on large
cap equity. The ETF currently has 318374.0m in AUM and 504 holdings. SPY tracks a market-cap-weighted index of US large- and
midcap stocks selected by the S\u0026P Committee.",
 "domicile": "US",
 "etfCompany": "SPDR",
 "expenseRatio": 0.0945,
 "inceptionDate": "1993-01-22",
 "investmentSegment": "Large Cap",
 "isin": "",
 "name": "SPDR S\u0026P 500 ETF Trust",
 "nav": 366.2784,
 "navCurrency": "USD",
 "priceToBook": 3.943968,
 "priceToEarnings": 26.82968,
 "trackingIndex": "S\u0026P 500",
 "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/etf_logo/spdr.png",
 "website": "https://us.spdrs.com/en/etf/spdr-sp-500-etf-SPY"
},
"symbol": "SPY"
}
```

## ETFs Holdings (Premium)

Python client: `finnhub_client.etfs_holdings(...)`

Get full ETF holdings/constituents. This endpoint has global coverage. Widget only shows top 10 holdings. A list of supported ETFs can be
found here.

Premium: Premium required.

**Arguments:**

symbol *(optional)*

ETF symbol.

isin *(optional)*
ETF isin.

skip *(optional)*
Skip the first n results. You can use this parameter to query historical constituents data. The latest result is returned if skip=0 or not set.

date optional param, not both.
Query holdings by date. You can use either this param or

**Response Attributes:**

atDate
Holdings update date.

holdings
Array of holdings.

assetType , , , , or empty.
Asset type. Can be 1 of the following values:

cusip
CUSIP.

isin
ISIN.

name
Security name

percent
Portfolio's percent

share
Number of shares owned by the ETF.

symbol
Symbol description

value
Market value

numberOfHoldings
Number of holdings.

symbol
ETF symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.etfs_holdings('SPY'))
```

Sample response (truncated):
```json
{
"atDate": "2023-03-24",
"holdings": [
    {
       "assetType": "Equity",
       "cusip": "88160R101",
       "isin": "US88160R1014",
       "name": "TESLA INC",
       "percent": 10.54,
      "share": 3971395,
      "symbol": "TSLA",
      "value": 763381546.9
   },
   {
      "assetType": "Equity",
      "cusip": "98980L101",
      "isin": "US98980L1017",
      "name": "ZOOM VIDEO COMMUNICATIONS-A",
      "percent": 8.05,
      "share": 8418916,
      "symbol": "ZM",
      "value": 582504798.04
   },
],
"numberOfHoldings": 28,
"symbol": "ARKK"
}
Widget:                         Etf Name                  Expense Ratio                              Number of Holdings  Inception Date
IVV Holdings                   iShares Core S&P 500 ETF  0.03                                       508                 2000-05-15
Portfolio Date
-10-21
Symbol           Holdings                                                                 Weight(%)  Market Value($)     Quantity
NVDA             NVIDIA                                                                   8.02059    $71,315,089,399.26  321,282,558
AAPL             APPLE                                                                    7.49587    $66,649,560,232.46  193,754,354
MSFT             MICROSOFT                                                                5.90897    $52,539,588,675.75  98,582,585
AMZN             AMAZON.COM INC                                                           3.84527    $34,190,188,226.64  130,312,872
GOOGL            ALPHABET CLASS A                                                         2.93309    $26,079,544,082.48  77,905,198
AVGO             BROADCOM INC                                                             2.39961    $21,336,165,487.2   63,162,124
GOOG             ALPHABET CLASS C                                                         2.34881    $20,884,483,917.5   63,104,650
META             META PLATFORMS CLASS A                                                   2.29659    $20,420,083,540.32  29,275,266
...
```

## ETFs Sector Exposure (Premium)

Python client: `finnhub_client.etfs_sector_exp(...)`

Get ETF sector exposure data.

**Arguments:**

symbol *(optional)*
ETF symbol.

isin *(optional)*
ETF isin.

**Response Attributes:**

sectorExposure
Array of industries and exposure levels.

exposure
Percent of exposure.

industry
Industry

symbol
ETF symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.etfs_sector_exp('SPY'))
```

Sample response:
```json
{
"sectorExposure": [
    {
       "exposure": 31.96,
       "industry": "Technology"
    },
    {
       "exposure": 14.79,
       "industry": "Healthcare"
   },
   {
      "exposure": 13.46,
      "industry": "Consumer Cyclicals"
   }
],
"symbol": "SPY"
}
```

## ETFs Country Exposure (Premium)

Python client: `finnhub_client.etfs_country_exp(...)`

Get ETF country exposure data.

**Arguments:**

symbol *(optional)*
ETF symbol.

isin *(optional)*
ETF isin.

**Response Attributes:**

countryExposure
Array of countries and and exposure levels.

country
Country

exposure
Percent of exposure.

symbol
ETF symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.etfs_country_exp('SPY'))
```

Sample response:
```json
{
"countryExposure": [
    {
       "country": "United States of America (the)",
       "exposure": 97.02
    },
    {
       "country": "Ireland",
       "exposure": 1.65
   },
   {
      "country": "United Kingdom of Great Britain and Northern Ireland (the)",
      "exposure": 0.88
   },
   {
      "country": "Switzerland",
      "exposure": 0.41
   },
   {
      "country": "Bermuda",
      "exposure": 0.03
   }
],
"symbol": "SPY"
}
```

## ETFs Equity Allocation (Premium)

Python client: `finnhub_client.etfs_allocation(...)`

Get ETF equity allocation based on the characteristics of the holdings.

**Arguments:**

symbol *(optional)*
ETF symbol.

isin *(optional)*
ETF isin.

**Response Attributes:**

data
ETF allocation.
largeBlend
Percentage of stocks classified as Large Blend.
largeGrowth
Percentage of stocks classified as Large Growth.
largeValue
Percentage of stocks classified as Large Value.
midBlend
Percentage of stocks classified as Mid-cap Blend.
midGrowth
Percentage of stocks classified as Mid-cap Growth.
midValue
Percentage of stocks classified as Mid-cap Value.
smallBlend
Percentage of stocks classified as Small-cap Blend.
smallGrowth
Percentage of stocks classified as Small-cap Growth.
smallValue
Percentage of stocks classified as Small-cap Value.
symbol
ETF symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.etfs_allocation('SPY'))
```

Sample response:
```json
{
"data": {
    "largeBlend": 38.1,
    "largeGrowth": 20.41,
    "largeValue": 22.03,
    "midBlend": 8.67,
    "midGrowth": 3.88,
    "midValue": 5.94,
    "smallBlend": 0.52,
   "smallGrowth": 0.05,
   "smallValue": 0.4
},
"symbol": "SPY"
}
```

## Mutual Funds Profile (Premium)

Python client: `finnhub_client.mutual_fund_profile(...)`

Get mutual funds profile information. This endpoint covers both US and global mutual funds. For international funds, you must query the data
using ISIN. A list of supported funds can be found here.

Premium: Premium required.

**Arguments:**

symbol *(optional)*
Fund's symbol.

isin *(optional)*
Fund's isin.

**Response Attributes:**

profile
Profile data.

benchmark
Index benchmark.

beta
Beta.

category
Fund's category.

classId
Class ID.

className
Class name.

currency
Fund's currency

cusip
CUSIP.

deferredLoad

Deferred load.

description
Fund's description.

expenseRatio
Expense ratio.

fee12b1
12B-1 fee.

frontLoad
Front Load.

fundCompany
Fund Company.

fundFamily
Fund Family.

inceptionDate
Inception date.

investmentSegment
Investment Segment.

iraMinInvestment
IRA minimum investment.

isin
ISIN.

manager
Fund's managers.

maxRedemptionFee
Max redemption fee.

name
Name

seriesId
Fund's series ID. This field can be used to group multiple share classes into 1 unique fund.

seriesName
Fund's series name.

sfdrClassification
SFDR classification for EU funds. Under the new classifications, a fund's strategy will labeled under either Article 6, 8 or 9. Article 6
covers funds which do not integrate any kind of sustainability into the investment process. Article 8, also known as `environmental and
socially promoting', applies "... where a financial product promotes, among other characteristics, environmental or social characteristics,
or a combination of those characteristics, provided that the companies in which the investments are made follow good governance
practices.". Article 9, also known as `products targeting sustainable investments', covers products targeting bespoke sustainable
investments and applies "... where a financial product has sustainable investment as its objective and an index has been designated as a
reference benchmark."

standardMinInvestment
Minimum investment for standard accounts.

status
Status.

totalNav
NAV.

turnover
Turnover.

symbol

Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_profile("VTSAX"))
```

Sample response:
```json
{
"profile": {
      "benchmark": "CRSP US Total Stock Market TR",
      "beta": 1.05,
      "category": "Multi-Cap Core",
      "cusip": "",
      "deferredLoad": 0,
      "description": "Created in 1992, Vanguard Total Stock Market Index Fund is designed to provide investors with exposure
to the entire U.S. equity market, including small-, mid-, and large-cap growth and value stocks. The fund's key attributes
are its low costs, broad diversification, and the potential for tax efficiency. Investors looking for a low-cost way to gain
broad exposure to the U.S. stock market who are willing to accept the volatility that comes with stock market investing may
wish to consider this fund as either a core equity holding or your only domestic stock fund.",
     "expenseRatio": 0.04,
     "fee12b1": 0,
     "frontLoad": 0,
     "fundFamily": "VANGUARD ADMIRAL",
     "inceptionDate": "2000-11-13",
     "investmentSegment": "Growth & Income",
     "iraMinInvestment": 0,
     "isin": "",
     "manager": "O'Reilly,Nejman",
     "maxRedemptionFee": 0,
     "name": "Vanguard Index Funds: Vanguard Total Stock Market Index Fund; Admiral Class Shares",
     "standardMinInvestment": 3000,
     "status": "Open",
     "totalNav": 280758000000,
"turnover": 8
},
"symbol": "VTSAX"
}
```

## Mutual Funds Holdings (Premium)

Python client: `finnhub_client.mutual_fund_holdings(...)`

Get full Mutual Funds holdings/constituents. This endpoint covers both US and global mutual funds. For international funds, you must query
the data using ISIN. A list of supported funds can be found here.
Premium: Premium required.

**Arguments:**

symbol *(optional)*
Fund's symbol.

isin *(optional)*

Fund's isin.

skip *(optional)*
Skip the first n results. You can use this parameter to query historical constituents data. The latest result is returned if skip=0 or not set.

**Response Attributes:**

atDate
Holdings update date.

holdings
Array of holdings.

assetType , , , , or empty.
Asset type. Can be 1 of the following values:

cusip
CUSIP.

isin
ISIN.

name
Security name

percent
Portfolio's percent

share
Number of shares.

symbol
Symbol description

value
Market value

numberOfHoldings
Number of holdings.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_holdings("VTSAX"))
```

Sample response:
```json
{
"atDate": "2023-01-31",
"holdings": [
    {
       "assetType": "Equity",
       "cusip": "037833100",
       "isin": "US0378331005",
       "name": "Apple Inc",
       "percent": 5.36984,
      "share": 463159883,
      "symbol": "AAPL",
      "value": 66829339518
   },
   {
      "assetType": "Equity",
      "cusip": "594918104",
      "isin": "US5949181045",
      "name": "Microsoft Corp",
      "percent": 4.54903,
      "share": 228457719,
      "symbol": "MSFT",
      "value": 56614107345
   }
],
"numberOfHoldings": 3972,
"symbol": "VTSAX"
}
```

## Mutual Funds Sector Exposure (Premium)

Python client: `finnhub_client.mutual_fund_country_exp(...)`

Get Mutual Funds sector exposure data.
Premium: Premium required.

**Arguments:**

symbol *(optional)*
Mutual Fund symbol.

isin *(optional)*
Fund's isin.

**Response Attributes:**

sectorExposure
Array of sector and exposure levels.

exposure
Percent of exposure.

sector
Sector

symbol
Mutual symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_sector_exp("VTSAX"))
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_country_exp("VTSAX"))
```

Sample response (truncated):
```json
{
"sectorExposure": [
    {
       "exposure": 26.2,
       "sector": "Information Technology"
    },
    {
       "exposure": 13.84,
       "sector": "Health Care"
   },
   {
      "exposure": 12.29,
      "sector": "Consumer Discretionary"
   },
   {
      "exposure": 10.46,
      "sector": "Financials"
   }
],
"symbol": "VTSAX"
}
Mutual Funds Country Exposure                                                Premium
Get Mutual Funds country exposure data.
Method:
Premium: Premium required.
Examples:
Arguments:
symbol optional
Symbol.
isin optional
Fund's isin.
Response Attributes:
countryExposure
Array of countries and and exposure levels.
country
Country
exposure
Percent of exposure.
symbol
...
```

## Mutual Funds EET (Premium)

Python client: `finnhub_client.mutual_fund_eet(...)`

Get EET data for EU funds. For PAIs data, please see the EET PAI endpoint.

**Arguments:**

isin *(REQUIRED)*
ISIN.

**Response Attributes:**

data
EET data.
isin
ISIN.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_eet("LU2036931686"))
```

Sample response:
```json
{    "data":{
        "boardGenderDiversityConsidered":true,
        "carbonFootprintScope123Considered":false,
        "carbonFootprintScope12Considered":false,
        "clientSustainabilityPreferencesConsidered":true,
        "controversialWeaponsConsidered":true,
        "energyConsumptionIntensityNACEAConsidered":false,
        "exposuretoEnergyEfficientRealEstateAssetsConsidered":false,
        "exposuretoFossilFuelSectorConsidered":false,
       "exposuretoFossilFuelsExtractionStorageTransportManufactureConsidered":false,
       "greenhouseGasEmissionsScope1Considered":false,
       "greenhouseGasEmissionsScope2Considered":false,
       "greenhouseGasEmissionsScope3Considered":false,

   },
   "isin":"LU2036931686"
}
```

## Mutual Funds EET PAI (Premium)

Python client: `finnhub_client.mutual_fund_eet_pai(...)`

Get EET PAI data for EU funds.

**Arguments:**

isin *(REQUIRED)*
ISIN.

**Response Attributes:**

data
EET data.

isin
ISIN.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.mutual_fund_eet_pai("LU2036931686"))
```

Sample response:
```json
{
    "data":{
     "airPollutantEmissionsCoveredHoldings":27.94263,
     "airPollutantEmissionsEligibleHoldings":490.89858,
     "airPollutantEmissionsNumberHoldingsCovered":14,
     "airPollutantEmissionsPctPortfolioCoverage":4.57,
     "airPollutantEmissionsPctPortfolioEligibleAssets":79.65,
     "airPollutantEmissionsTonnesPerEURm":1.28271,
     "antiHumanTraffickingNumberHoldingsCovered":67,
},
"isin":"LU2036931686"
}
```

## Bond Profile (Premium)

Python client: `finnhub_client.bond_profile(...)`

Get general information of a bond. You can query by FIGI, ISIN or CUSIP. A list of supported bonds can be found here.

**Arguments:**

isin *(optional)*
ISIN

cusip *(optional)*
CUSIP

figi *(optional)*
FIGI

**Response Attributes:**

amountOutstanding
Outstanding amount.
asset
Asset.
assetType
Asset.
bondType
Bond type.
callable
Callable.
coupon
Coupon.
couponType
Coupon type.
cusip

Cusip.

datedDate
Dated date.

debtType
Bond type.

figi
FIGI.

firstCouponDate
First coupon date.

industryGroup
Industry.

industrySubGroup
Sub-Industry.

isin
ISIN.

issueDate
Issue date.

maturityDate
Period.

offeringPrice
Offering price.

originalOffering
Offering amount.

paymentFrequency
Payment frequency.

securityLevel
Security level.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.bond_profile(isin='US912810TD00'))
```

Sample response:
```json
{                                                                  Delay
End-of-day
"isin":"US912810TD00",                                                                Delayed 4h
Delayed 4h
"cusip":"",                                                       End-of-day
"figi":"BBG0152KFHS6",
"coupon":2.25,
"maturityDate":"2052-02-15",
"offeringPrice":100,
"issueDate":"2022-03-15",
"bondType":"US Government",
"debtType":"",
"industryGroup":"Government",
"industrySubGroup":"U.S. Treasuries",
"asset":"",
"assetType":"",
"datedDate":"2022-02-15",
"firstCouponDate":"2022-08-15",
"originalOffering":20000000000,
"amountOutstanding":36914000000,
"paymentFrequency":"Semi-Annual",
"securityLevel":"",
"callable":null,
"couponType":"",
"dayCount":""
}
Bond price data Premium
Get bond's price data. The following datasets are supported:
Exchange                                 Segment
```

## US Government Bonds (Free)

Python client: `finnhub_client.bond_price(...)`

FINRA Trace BTDS: US Corporate Bonds
FINRA Trace 144A Bonds
International Bonds International Bonds

**Arguments:**

isin *(REQUIRED)*
ISIN.

from *(REQUIRED)*
UNIX timestamp. Interval initial value.

to *(REQUIRED)*
UNIX timestamp. Interval end value.

**Response Attributes:**

c
List of close prices for returned candles.

s
Status of the response. This field can either be ok or no_data.

t

List of timestamp for returned candles.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.bond_price('US912810TD00', 1590988249, 1649099548))
```

Sample response:
```json
{
"c":[
    97.5,
    97.96875,
    98.78125,
],
"s":"ok",
"t":[
    1644883200,
   1644969600,
   1645056000,
]
}
```

## Bond Tick Data (Premium)

Python client: `finnhub_client.bond_tick(...)`

Get trade-level data for bonds. The following datasets are supported:

Exchange Segment Delay
Delayed 4h
FINRA Trace BTDS: US Corporate Bonds Delayed 4h
FINRA Trace 144A Bonds

**Arguments:**

isin *(REQUIRED)*
ISIN.

date *(REQUIRED)*
Date: 2020-04-02.

limit *(REQUIRED)*
Limit number of ticks returned. Maximum value:

skip *(REQUIRED)*
Number of ticks to skip. Use this parameter to loop through the entire data.

exchange *(REQUIRED)*

Currently support the following values: .

**Response Attributes:**

ats

ATS flag. Y or empty

c
List of trade conditions. A comprehensive list of trade conditions code can be found here

count < , all data for that date has been returned.
Number of ticks returned. If

cp
List of values showing the counterparty of each trade. List of supported values: here

p
List of price data.

rp
List of values showing the reporting party of each trade. List of supported values: here

si
List of values showing the side (Buy/sell) of each trade. List of supported values: here

skip
Number of ticks skipped.

t
List of timestamp in UNIX ms.

total
Total number of ticks for that date.

v
List of volume data.

y
List of yield data.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.bond_tick('US693475BF18', '2022-08-19', 500, 0, 'trace'))
```

Sample response:
```json
{
    "c":[[],[],[]],
    "count":3,
    "cp":[
        "3",
        "1",
        "1"
    ],
    "p":[
       100.592,
       100.492,
       100.234
],
"si":[
       "2",
       "2",
       "2"
],
"skip":6,
"t":[
       1660929161000,
       1660929161000,
       1660929778000
],
"total":211,
"v":[
       3000,
       3000,
       50000
]
}
```

## Bond Yield Curve (Premium)

Python client: `finnhub_client.bond_yield_curve(...)`

Get yield curve data for Treasury bonds.

**Arguments:**

code *(REQUIRED)*
Bond's code. You can find the list of supported code here.

**Response Attributes:**

code
Bond's code
data
Array of data.
d
Date of the reading
v
Value

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.bond_yield_curve('10y'))
```

Sample response:
```json
{
"code": "10y",
"data": [
    {
       "d": "2022-10-31",
       "v": 4.1
    },
    {
       "d": "2022-11-01",
      "v": 4.07
   }
]
}
Forex Exchanges
```

## List supported forex exchanges (Free)

Python client: `finnhub_client.forex_exchanges(...)`

**Arguments:**

**Response Attributes:**

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.forex_exchanges())
```

Sample response:
```json
[
"oanda",
"fxcm",
"forex.com",
"ic markets",
"fxpro"
]
```

## Forex Symbol (Free)

Python client: `finnhub_client.forex_symbols(...)`

List supported forex symbols.

**Arguments:**

exchange *(REQUIRED)*
Exchange you want to get the list of symbols from.

Response Attributes: endpoint.

description
Symbol description

displaySymbol
Display symbol name.

symbol
Unique symbol used to identify this symbol used in

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.forex_symbols('OANDA'))
```

Sample response:
```json
[
{
    "description": "IC MARKETS Euro vs US Dollar EURUSD",
    "displaySymbol": "EUR/USD",
    "symbol": "IC MARKETS:1"
},
{
    "description": "IC MARKETS Australian vs US Dollar AUDUSD",
    "displaySymbol": "AUD/USD",
   "symbol": "IC MARKETS:5"
},
{
   "description": "IC MARKETS British Pound vs US Dollar GBPUSD",
   "displaySymbol": "GBP/USD",
   "symbol": "IC MARKETS:2"
}]
```

## Forex Candles (Premium)

Python client: `finnhub_client.forex_candles(...)`

Get candlestick data for forex symbols.

Arguments: endpoint for this field.

symbol *(REQUIRED)*
Use symbol returned in

resolution REQUIRED .Some timeframes might not be available depending on the exchange.

Supported resolution includes

from *(REQUIRED)*
UNIX timestamp. Interval initial value.

to *(REQUIRED)*
UNIX timestamp. Interval end value.

**Response Attributes:**

c
List of close prices for returned candles.

h
List of high prices for returned candles.

l
List of low prices for returned candles.

o
List of open prices for returned candles.

s
Status of the response. This field can either be ok or no_data.

t
List of timestamp for returned candles.

v
List of volume data for returned candles.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.forex_candles('OANDA:EUR_USD', 'D', 1590988249, 1591852249))
```

Sample response (truncated):
```json
{
"c": [
       1.10713,
       1.10288,
       1.10397,
       1.10182
],
"h": [
       1.1074,
      1.10751,
      1.10729,
      1.10595
],
"l": [
      1.09897,
      1.1013,
      1.10223,
      1.10101
],
"o": [
      1.0996,
      1.107,
      1.10269,
      1.10398
],
"s": "ok",
"t": [
      1568667600,
      1568754000,
      1568840400,
      1568926800
],
"v": [
      75789,
      75883,
      73485,
      5138
]
}
Widget:
...
```

## Get rates for all forex pairs. Ideal for currency conversion (Free)

Python client: `finnhub_client.forex_rates(...)`

**Arguments:**

base *(optional)*
Base currency. Default to EUR.

date *(optional)*
Date. Leave blank to get the latest data.

**Response Attributes:**

base
Base currency.
quote
A map of base/quote rates for all currency pair.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.forex_rates(base='USD'))
```

Sample response:
```json
{
"base": "USD",
"quote": {
    "AED": 3.968012,
    "AFN": 82.373308,
    "ALL": 124.235408,
    "AMD": 520.674275,
    "CAD": 1.525368,
    "CDF": 1904.576741,
   "CHF": 1.053259,
   "CNY": 7.675235,
   "COP": 4282.32676,
   "CRC": 614.796995,
   "CUC": 1.080304,
   "CUP": 28.628067,
   "CVE": 110.517004,
   "CZK": 27.096737,
   "DJF": 191.991344,
   "DKK": 7.461229,
   "DOP": 59.195018,
   "DZD": 139.384021,
   "EGP": 17.018597,
   "ERN": 16.204913,
   "ETB": 36.296767,
   "EUR": 0.91,
   "GBP": 0.874841,
   "JPY": 114.583548,
   "MDL": 19.120251,
   "MGA": 4105.156776,
   "USD": 1,
}
}
Crypto Exchanges
```

## List supported crypto exchanges (Free)

Python client: `finnhub_client.crypto_exchanges(...)`

**Arguments:**

**Response Attributes:**

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.crypto_exchanges())
```

Sample response:
```json
[
"KRAKEN",
"HITBTC",
"COINBASE",
"GEMINI",
"POLONIEX",
"Binance",
"ZB",
"BITTREX",
"KUCOIN",
"OKEX",
"BITFINEX",
"HUOBI"
]
Crypto Symbol
```

## List supported crypto symbols by exchange (Free)

Python client: `finnhub_client.crypto_symbols(...)`

**Arguments:**

exchange *(REQUIRED)*
Exchange you want to get the list of symbols from.

**Response Attributes:**

description
Symbol description
displaySymbol
Display symbol name.

symbol

Unique symbol used to identify this symbol used in endpoint.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.crypto_symbols('BINANCE'))
```

Sample response:
```json
[
{
    "description": "Binance ETHBTC",
    "displaySymbol": "ETH/BTC",
    "symbol": "ETHBTC"
},
{
    "description": "Binance LTCBTC",
    "displaySymbol": "LTC/BTC",
   "symbol": "BINANCE:LTCBTC"
},
{
   "description": "Binance BNBBTC",
   "displaySymbol": "BNB/BTC",
   "symbol": "BINANCE:BNBBTC"
}]
```

## Crypto Profile (Premium)

Python client: `finnhub_client.crypto_profile(...)`

Get crypto's profile.

**Arguments:**

symbol *(REQUIRED)*
Crypto symbol such as BTC or ETH.

**Response Attributes:**

circulatingSupply
Circulating supply.
description
Description.
launchDate
Launch date.
logo
Logo image.
longName

Long name.

marketCap
Market capitalization.

maxSupply
Max supply.

name
Name.

proofType
Proof type.

totalSupply
Total supply.

website
Project's website.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.crypto_profile('BTC'))
```

Sample response:
```json
{
"name": "Bitcoin",
"longName": "Bitcoin (BTC)",
"description": "Bitcoin uses peer-to-peer technology to operate with no central authority or banks; managing transactions
and the issuing of bitcoins is carried out collectively by the network. Although other cryptocurrencies have come before,
Bitcoin is the first decentralized cryptocurrency - Its reputation has spawned copies and evolution in the space.With the
largest variety of markets and the biggest value - having reached a peak of 318 billion USD - Bitcoin is here to stay. As
with any new invention, there can be improvements or flaws in the initial model however the community and a team of
dedicated developers are pushing to overcome any obstacle they come across. It is also the most traded cryptocurrency and
one of the main entry points for all the other cryptocurrencies. The price is as unstable as always and it can go up or down
by 10%-20% in a single day.Bitcoin is an SHA-256 POW coin with almost 21,000,000 total minable coins. The block time is 10
minutes. See below for a full range of Bitcoin markets where you can trade US Dollars for Bitcoin, crypto to Bitcoin and
many other fiat currencies too.Bitcoin Whitepaper PDF - A Peer-to-Peer Electronic Cash SystemBlockchain data provided by:
Blockchain (main source), Blockchair (backup)",
"marketCap": 1119891535870.4905,
"totalSupply": 18876550,
"maxSupply": 21000000,
"circulatingSupply": 18876550,
"logo": "",
"launchDate": "2009-01-03",
"website": "https://bitcoin.org/en/",
"proofType": "PoW"
}
```

## Crypto Candles (Premium)

Python client: `finnhub_client.crypto_candles(...)`

Get candlestick data for crypto symbols.

**Arguments:**

symbol REQUIRED endpoint for this field.

Use symbol returned in

resolution REQUIRED .Some timeframes might not be available depending on the exchange.
Supported resolution includes

from *(REQUIRED)*
UNIX timestamp. Interval initial value.

to *(REQUIRED)*
UNIX timestamp. Interval end value.

**Response Attributes:**

c
List of close prices for returned candles.

h
List of high prices for returned candles.

l
List of low prices for returned candles.

o
List of open prices for returned candles.

s
Status of the response. This field can either be ok or no_data.

t
List of timestamp for returned candles.

v
List of volume data for returned candles.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.crypto_candles('BINANCE:BTCUSDT', 'D', 1590988249, 1591852249))
```

Sample response:
```json
{
"c": [
       1.10713,
       1.10288,
       1.10397,
       1.10182
],
"h": [
       1.1074,
      1.10751,
      1.10729,
      1.10595
],
"l": [
      1.09897,
      1.1013,
      1.10223,
      1.10101
],
"o": [
      1.0996,
      1.107,
      1.10269,
      1.10398
],
"s": "ok",
"t": [
      1568667600,
      1568754000,
      1568840400,
      1568926800
],
"v": [
      75789,
      75883,
      73485,
      5138
]
}
Widget:
```

## Pattern Recognition (Premium)

Python client: `finnhub_client.pattern_recognition(...)`

Run pattern recognition algorithm on a symbol. Support double top/bottom, triple top/bottom, head and shoulders, triangle, wedge, channel,
flag, and candlestick patterns.

Examples: .Some timeframes might not be available depending on the exchange.

**Arguments:**

symbol *(REQUIRED)*
Symbol

resolution *(REQUIRED)*
Supported resolution includes

**Response Attributes:**

points
Array of patterns.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.pattern_recognition('AAPL', 'D'))
```

Sample response (truncated):
```json
"points": [
    {
       "aprice": 1.09236,
       "atime": 1567458000,
       "bprice": 1.1109,
       "btime": 1568322000,
       "cprice": 1.09897,
       "ctime": 1568667600,
       "dprice": 0,
      "dtime": 0,
      "end_price": 1.1109,
      "end_time": 1568926800,
      "entry": 1.1109,
      "eprice": 0,
      "etime": 0,
      "mature": 0,
      "patternname": "Double Bottom",
      "patterntype": "bullish",
      "profit1": 1.1294,
      "profit2": 0,
      "sortTime": 1568926800,
      "start_price": 1.1109,
      "start_time": 1566853200,
      "status": "incomplete",
      "stoploss": 1.0905,
      "symbol": "EUR_USD",
      "terminal": 0
   },
   {
      "aprice": 1.09236,
      "atime": 1567458000,
      "bprice": 1.1109,
      "btime": 1568322000,
      "cprice": 1.09897,
      "ctime": 1568667600,
      "dprice": 1.13394884,
      "dtime": 1568926800,
      "entry": 1.1339,
      "mature": 0,
      "patternname": "Bat",
...
```

## Support/Resistance (Premium)

Python client: `finnhub_client.support_resistance(...)`

Get support and resistance levels for a symbol.

**Arguments:**

symbol REQUIRED .Some timeframes might not be available depending on the exchange.

Symbol

resolution *(REQUIRED)*
Supported resolution includes

**Response Attributes:**

levels
Array of support and resistance levels.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.support_resistance('AAPL', 'D'))
```

Sample response:
```json
{
"levels": [
    1.092360019683838,
    1.1026300191879272,
    1.113450050354004,
    1.1233500242233276,
    1.134719967842102,
    1.1513700485229492
]
}
```

## Aggregate Indicators (Premium)

Python client: `finnhub_client.aggregate_indicator(...)`

Get aggregate signal of multiple technical indicators such as MACD, RSI, Moving Average v.v. A full list of indicators can be found here.

Arguments: .Some timeframes might not be available depending on the exchange.

symbol *(REQUIRED)*
symbol

resolution *(REQUIRED)*
Supported resolution includes

**Response Attributes:**

technicalAnalysis
Number of indicator signals strong buy, buy, neutral, sell, strong sell signals.

count
Number of indicators for each signal

buy

Number of buy signals

neutral
Number of neutral signals

sell
Number of sell signals

signal
Aggregate Signal

trend
Whether the market is trending.

adx
ADX reading

trending
Whether market is trending or going sideway

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.aggregate_indicator('AAPL', 'D'))
```

Sample response:
```json
{
"technicalAnalysis": {
    "count": {
    "buy": 6,
    "neutral": 7,
    "sell": 4
    },
    "signal": "neutral"
},
"trend": {
   "adx": 24.46020733373421,
   "trending": false
}
}
```

## Technical Indicators (Premium)

Python client: `finnhub_client.technical_indicator(...)`

Return technical indicator with price data. List of supported indicators can be found here.

**Arguments:**

symbol *(REQUIRED)*
symbol

resolution REQUIRED .Some timeframes might not be available depending on the exchange.

Supported resolution includes

from *(REQUIRED)*
UNIX timestamp. Interval initial value.

to *(REQUIRED)*
UNIX timestamp. Interval end value.

indicator *(REQUIRED)*
Indicator name. Full list can be found here.

indicator_fields *(optional)*
Check out this page to see which indicators and params are supported.

**Response Attributes:**

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.technical_indicator(symbol="AAPL", resolution='D', _from=1583098857, to=1584308457, indicator='rsi',
indicator_fields={"timeperiod": 3}))
```

Sample response:
```json
{"sma":[0,0,74.23916,73.74833,73.72416,70.676666,70.045,68.911,67.41666,66.802],"t":
[1583107200,1583193600,1583280000,1583366400,1583452800,1583712000,1583798400,1583884800,1583971200,1584057600]}
```

## Earnings Call Transcripts List (Premium)

Python client: `finnhub_client.transcripts_list(...)`

List earnings call transcripts' metadata. This endpoint is available for Global companies. You can get a list of supported symbols here
Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Company symbol: AAPL. Leave empty to list the latest transcripts

**Response Attributes:**

symbol
Company symbol.
transcripts
Array of transcripts' metadata

id

Transcript's ID used to get the full transcript.

quarter
Quarter of earnings result in the case of earnings call transcript.

time
Time of the event.

title
Title.

year
Year of earnings result in the case of earnings call transcript.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.transcripts_list('AAPL'))
```

Sample response (truncated):
```json
{
"symbol": "AAPL",
"transcripts": [
        {
           "id": "AAPL_326091",
           "quarter": 1,
           "symbol": "AAPL",
           "time": "2020-01-28 21:35:45",
           "title": "AAPL - Earnings Call Transcript Q1 2020",
          "year": 2020
       },
       {
          "id": "AAPL_322579",
          "quarter": 4,
          "symbol": "AAPL",
          "time": "2019-10-30 22:27:15",
          "title": "AAPL - Earnings Call Transcript Q4 2019",
          "year": 2019
       },
       {
          "id": "AAPL_318112",
          "quarter": 3,
          "symbol": "AAPL",
          "time": "2019-07-30 22:26:28",
          "title": "AAPL - Earnings Call Transcript Q3 2019",
          "year": 2019
       },
       {
          "id": "AAPL_313737",
          "quarter": 2,
          "symbol": "AAPL",
          "time": "2019-04-30 19:55:19",
          "title": "AAPL - Earnings Call Transcript Q2 2019",
          "year": 2019
       },
       {
          "id": "AAPL_308757",
          "quarter": 1,
          "symbol": "AAPL",
          "time": "2019-01-29 21:06:06",
...
```

## Earnings Call Transcripts (Premium)

Python client: `finnhub_client.transcripts(...)`

Get earnings call transcripts, audio and participants' list. Data is available for US, UK, European, Australian and Canadian companies.
15+ years of data is available with 220,000+ audio which add up to 7TB in size.
Premium: Premium required.

**Arguments:**

id *(REQUIRED)*
Transcript's id obtained with Transcripts List endpoint.

**Response Attributes:**

audio
Audio link.

id
Transcript's ID.

participant
Participant list

description
Participant's description

name
Participant's name

role
Whether the speak is a company's executive or an analyst

quarter
Quarter of earnings result in the case of earnings call transcript.

symbol
Company symbol.

time
Time of the event.

title
Title.

transcript
Transcript content.

name
Speaker's name

session
Earnings calls section (management discussion or Q&A)

speech
Speaker's speech

year
Year of earnings result in the case of earnings call transcript.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.transcripts('AAPL_162777'))
```

Sample response (truncated):
```json
{
"audio": "https://static.finnhub.io/transcripts_audio/4319666.mp3",
"id": "AAPL_326091",
"participant": [
            {
               "name": "Tejas Gala",
               "description": "Senior Analyst at Corporate Finance and IR"
            },
            {
              "name": "Tim Cook",
              "description": "CEO"
           }
],
"quarter": 1,
"symbol": "AAPL",
"time": "2020-01-28 21:35:45",
"title": "AAPL - Earnings call transcripts Q1 2020",
"transcript": [
           {
              "name": "Operator",
              "speech": [
                 "Good day, everyone. Welcome to the Apple Incorporated First Quarter Fiscal Year 2020 Earnings Conference Call.
Today's conference is being recorded. At this time for opening remarks and introductions, I would like to turn the call over
to Tejas Gala, Senior Analyst, Corporate Finance and Investor Relations. Please go ahead."
              ]
           },
           {
              "name": "Tejas Gala",
              "speech": [
                 "Thank you. Good afternoon, and thank you for joining us. Speaking first today is Apple's CEO, Tim Cook, and he'll
be followed by CFO, Luca Maestri. After that, we'll open the call to questions from analysts. Please note that some of the
information you'll hear during our discussion today will consist of forward-looking statements, including without
limitation, those regarding revenue, gross margin, operating expenses, other income and expenses, taxes, capital allocation
and future business outlook. Actual results or trends could differ materially from our forecast. For more information, please
refer to the risk factors discussed in Apple's most recently filed periodic reports on Form 10-K and Form 10-Q and the Form 8-K
filed with the SEC today, along with the associated press release. Apple assumes no obligation to update any forward-looking
statements or information, which speaks as of their respective dates. I'd now like to turn the call over to Tim for introductory
remarks."
]
}
...
```

## Earnings Call Audio Live (Premium)

Python client: `finnhub_client.earnings_call_live(...)`

Stream live earnings calls with data provided in the calendar. The data will be available in m3u8 format. mp3 files will be available once the

calls finish in the field.

Premium: Premium required.

**Arguments:**

from *(optional)*

From date .

to *(optional)*

To date .

symbol *(optional)*
Filter by symbol: AAPL.

**Response Attributes:**

event
Array of earnings call events that support live streaming.

event
Event name.

liveAudio
Live audio streaming file.

quarter
Earnings quarter.

recording
Recoding in mp3 format.

symbol
Symbol.

time
Date time in UTC.

year
Earnings year.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.earnings_call_live("2024-11-01", "2024-11-30"))
```

Sample response:
```json
{
"event": [
       {
           "symbol": "NVDA",
           "year": 2025,
           "quarter": 3,
           "event": "NVDA - Earnings call Q3 year",
           "time": "2024-11-20 22:00:00",
           "liveAudio": "https://live.finnhub.io/hls/2063191eb8563e1645fe3bde2b057511dce4f8a0fb39a2fb9/audio.m3u8",
          "recording": ""
      },
      {
          "symbol": "SNOW",
          "year": 2025,
          "quarter": 3,
          "event": "SNOW - Earnings call Q3 year",
          "time": "2024-11-20 22:00:00",
          "liveAudio": "https://live.finnhub.io/hls/869c16f0fe27d972d49b511f18eea69499c6f0c460a28/audio.m3u8",
          "recording": ""
      }
]
}
```

## Company Presentation (Premium)

Python client: `finnhub_client.stock_presentation(...)`

Get presentations/slides data in PDF format that are usually used during earnings calls. You can get a list of supported symbols here
Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

**Response Attributes:**

res
Presentation data.

atTime
At Time.

quarter
Quarter

title
Title

url
Presentation url

year
Year

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_presentation('IBM'))
```

Sample response:
```json
{
"res": [
       {
           "atTime": "2025-01-29 22:00:00",
           "quarter": 4,
           "title": "IBM Q4 2024",
           "url": "https://finnhub.io/api/redirect?urlType=transcripts-slides2&id=d244c28ec5ee4767b2",
           "year": 2024
       },
      {
          "atTime": "2024-10-23 21:00:00",
          "quarter": 3,
          "title": "IBM Q3 2024",
          "url": "https://finnhub.io/api/redirect?urlType=transcripts-slides2&id=491dc513be934082f1",
          "year": 2024
      }
],
"symbol": "IBM"
}
```

## Social Sentiment (Premium)

Python client: `finnhub_client.stock_social_sentiment(...)`

Get social sentiment for stocks on Reddit and Twitter.
Premium: Premium required.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

from *(optional)*

From date .

to *(optional)*

To date .

**Response Attributes:**

data
Sentiment data.

atTime
Period.

mention
Number of mentions

negativeMention
Number of negative mentions

negativeScore
Negative score. Range 0-1

positiveMention
Number of positive mentions

positiveScore

Positive score. Range 0-1

score
Final score. Range: -1 to 1 with 1 is very positive and -1 is very negative

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_social_sentiment('GME'))
```

Sample response:
```json
{
"data": [
    {
       "atTime": "2021-05-08 14:00:00",
       "mention": 32,
       "positiveScore": 0.9213675,
       "negativeScore": -0.9864475,
       "positiveMention": 20,
       "negativeMention": 12,
      "score": -0.0341123222115352
   },
   {
      "atTime": "2021-05-08 13:00:00",
      "mention": 25,
      "positiveScore": 0.92,
      "negativeScore": -0.991266,
      "positiveMention": 8,
      "negativeMention": 17,
      "score": -0.56282
   }
],
"symbol": "AAPL"
}
```

## Investment Themes (Thematic Investing) (Premium)

Python client: `finnhub_client.stock_investment_theme(...)`

Thematic investing involves creating a portfolio (or portion of a portfolio) by gathering together a collection of companies involved in certain
areas that you predict will generate above-market returns over the long term. Themes can be based on a concept such as ageing populations
or a sub-sector such as robotics, and drones. Thematic investing focuses on predicted long-term trends rather than specific companies or
sectors, enabling investors to access structural, one-off shifts that can change an entire industry.

This endpoint will help you get portfolios of different investment themes that are changing our life and are the way of the future.

A full list of themes supported can be found here. The theme coverage and portfolios are updated bi-weekly by our analysts. Our approach
excludes penny, super-small cap and illiquid stocks.

**Arguments:**

theme *(REQUIRED)*
Investment theme. A full list of themes supported can be found here.

**Response Attributes:**

data
Investment theme portfolio.

symbol
Symbol

theme
Investment theme

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_investment_theme('financialExchangesData'))
```

Sample response:
```json
{
"data": [
    {
       "symbol": "ICE"
    },
    {
       "symbol": "NDAQ"
    },
    {
      "symbol": "CBOE"
   },
   {
      "symbol": "FDS"
   },
   {
      "symbol": "SPGI"
   },
   {
      "symbol": "TW"
   }
],
"theme": "financialExchangesData"
}
```

## Supply Chain Relationships (Premium)

Python client: `finnhub_client.stock_supply_chain(...)`

This endpoint provides an overall map of public companies' key customers and suppliers. The data offers a deeper look into a company's
supply chain and how products are created. The data will help investors manage risk, limit exposure or generate alpha-generating ideas and
trading insights.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

data
Key customers and suppliers.

country
Country

customer
Whether the company is a customer.

industry
Industry

name
Name

oneMonthCorrelation
1-month price correlation

oneYearCorrelation
1-year price correlation

sixMonthCorrelation
6-month price correlation

supplier
Whether the company is a supplier

symbol
Symbol

threeMonthCorrelation
3-month price correlation

twoWeekCorrelation
2-week price correlation

twoYearCorrelation
2-year price correlation

symbol
symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_supply_chain('AAPL'))
```

Sample response (truncated):
```json
{
"data": [
    {
       "customer": true,
       "name": "Costco Wholesale Corporation",
       "oneMonthCorrelation": 0.26,
       "oneYearCorrelation": 0.63,
       "sixMonthCorrelation": 0.87,
       "supplier": false,
      "symbol": "COST",
      "threeMonthCorrelation": 0.89,
      "twoWeekCorrelation": 0.35,
      "twoYearCorrelation": 0.91
   },
   {
      "customer": true,
      "name": "Qualcomm",
      "oneMonthCorrelation": 0.06,
      "oneYearCorrelation": 0.58,
      "sixMonthCorrelation": 0.87,
      "supplier": true,
      "symbol": "QCOM",
      "threeMonthCorrelation": 0.88,
      "twoWeekCorrelation": 0.71,
      "twoYearCorrelation": 0.94
   },
   {
      "customer": false,
      "name": "Foxconn Industrial Internet Co., Ltd.",
      "oneMonthCorrelation": 0.25,
      "oneYearCorrelation": -0.48,
      "sixMonthCorrelation": -0.65,
      "supplier": true,
      "symbol": "601138.SS",
      "threeMonthCorrelation": -0.79,
      "twoWeekCorrelation": -0.55,
      "twoYearCorrelation": -0.6
   }
],
"symbol": "AAPL"
...
```

## Company ESG Scores (Premium)

Python client: `finnhub_client.company_esg_score(...)`

This endpoint provides the latest ESG scores and important indicators for 7000+ global companies. The data is collected through company's
public ESG disclosure and public sources.

Our ESG scoring models takes into account more than 150 different inputs to calculate the level of ESG risks and how well a company is
managing them. A higher score means lower ESG risk or better ESG management. ESG scores are in the the range of 0-100. Some key
indicators might contain letter-grade score from C- to A+ with C- is the lowest score and A+ is the highest score.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

data

Map key-value pair of key ESG data points.

environmentScore
Environment Score

governanceScore
Governance Score

socialScore
Social Score

symbol
symbol

totalESGScore
Total ESG Score

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_esg_score("AAPL"))
```

Sample response (truncated):
```json
{
"data": {
    "womenManagementPercentage": 17.02,
    "adultContent": false,
    "alcoholic": false,
    "animalTesting": false,
    "antitrust": "C+",
    "asianEmployeePercentage": 27,
    "asianManagementPercentage": 27,
   "blackEmployeePercentage": 9,
   "blackManagementPercentage": 4,
   "carbonReductionPolicy": null,
   "catholic": false,
   "climateStrategy": "A+",
   "co2EmissionScope1": 47430,
   "co2EmissionScope2": 890189,
   "co2EmissionScope3": 22648000,
   "co2EmissionTotal": 937619,
   "coalEnergy": false,
   "ecofriendlyPackaging": null,
   "environmentalReporting": true,
   "firearms": false,
   "fuelEfficiencyConsumption": null,
   "furLeather": false,
   "gambling": false,
   "gmo": false,
   "hazardousSubstances": null,
   "hispanicLatinoEmployeePercentage": 14,
   "hispanicLatinoManagementPercentage": 8,
   "humanRightsPolicy": "C-",
   "militaryContract": false,
   "nuclear": false,
   "palmOil": false,
   "pesticides": false,
   "privacyPolicy": "B-",
   "recallPolicySafety": null,
   "recyclingPolicy": null,
   "stakeholderEngagement": null,
   "sustainableForestryPolicy": null,
   "tobacco": false,
...
```

## Historical ESG Scores (Premium)

Python client: `finnhub_client.company_historical_esg_score(...)`

This endpoint provides historical ESG scores and important indicators for 7000+ global companies. The data is collected through company's
public ESG disclosure and public sources.

Our ESG scoring models takes into account more than 150 different inputs to calculate the level of ESG risks and how well a company is
managing them. A higher score means lower ESG risk or better ESG management. ESG scores are in the the range of 0-100. Some key
indicators might contain letter-grade score from C- to A+ with C- is the lowest score and A+ is the highest score.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

data
Historical ESG data points.

data
Map key-value pair of key ESG data points.

environmentScore
Environment Score

governanceScore
Governance Score

period
Period

socialScore
Social Score

totalESGScore
Total ESG Score

symbol
symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_historical_esg_score("AAPL"))
```

Sample response (truncated):
```json
{
"data": [
    {
       "data": {
        "adultContent": false,
        "alcoholic": false,
        "animalTesting": false,
        "antitrust": "62.0",
        "asianEmployeePercentage": 27.9,
       "asianManagementPercentage": 29.2,
       "blackEmployeePercentage": 9.4,
       "blackManagementPercentage": 4,
       "carbonReductionPolicy": "True",
       "catholic": true,
       "co2EmissionScope1": 55202,
       "co2EmissionScope2": 1003246,
       "co2EmissionScope3": 23128420,
       "co2EmissionTotal": 1058448,
       "coalEnergy": false
      },
      "environmentScore": 61.74593,
      "governanceScore": 92.81813,
      "period": "2021-09-25",
      "socialScore": 76.52558,
      "totalESGScore": 77.02988
   },
   {
      "data": {
       "adultContent": false,
       "alcoholic": false,
       "animalTesting": false,
       "antitrust": "28.0",
       "asianEmployeePercentage": 27,
       "asianManagementPercentage": 27,
       "blackEmployeePercentage": 9,
       "blackManagementPercentage": 4,
       "carbonReductionPolicy": "True",
       "catholic": true,
       "co2EmissionScope1": 47430,
       "co2EmissionScope2": 890189,
...
```

## Profitability (Free)

Python client: `finnhub_client.company_earnings_quality_score(...)`

Growth
Cash Generation & Capital Allocation
Leverage

We then compare the metrics of each company in each category against its peers in the same industry to gauge how quality its earnings is.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

freq *(REQUIRED)*

Frequency. Currently support and

**Response Attributes:**

data
Array of earnings quality score.

cashGenerationCapitalAllocation
Cash Generation and Capital Allocation

growth
Growth Score

letterScore
Letter Score

leverage
Leverage Score

period
Period

profitability
Profitability Score

score
Total Score

freq
Frequency

symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.company_earnings_quality_score('AAPL', 'quarterly'))
```

Sample response:
```json
{
"data": [
       {
          "capitalAllocation": 67.6878,
          "growth": 55.8022,
          "letterScore": "B+",
          "leverage": 24.5122,
          "period": "2021-06-01",
          "profitability": 82.3843,
         "score": 57.5966
      },
      {
         "capitalAllocation": 75.1464,
         "growth": 70.2461,
         "letterScore": "A-",
         "leverage": 39.5682,
         "period": "2021-03-01",
         "profitability": 88.4613,
         "score": 68.3555
      },
      {
         "capitalAllocation": 43.8708,
         "growth": 68.1803,
         "letterScore": "A-",
         "leverage": 56.1926,
         "period": "2020-12-01",
         "profitability": 92.6311,
         "score": 65.2187
      },
],
"freq": "quarterly",
"symbol": "AAPL"
}
```

## USPTO Patents (Free)

Python client: `finnhub_client.stock_uspto_patent(...)`

List USPTO patents for companies. Limit to 250 records per API call.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data
Array of patents.

applicationNumber
Application Number.

companyFilingName
Array of companies' name on the patent.

description

Description.

filingDate
Filing date.

filingStatus
Filing status.

patentNumber
Patent number.

patentType
Patent's type.

publicationDate
Publication date.

url
URL of the original article.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_uspto_patent('NVDA', _from="2020-06-01", to="2021-06-10"))
```

Sample response:
```json
{    "data":[
        {
             "applicationNumber":"17163855",
             "companyFilingName":[
                  "NVIDIA CORPORATION"
             ],
             "description":"DYNAMIC DIRECTIONAL ROUNDING",
             "filingDate":"2021-02-01 00:00:00",
             "filingStatus":"Application",
            "patentNumber":"US20210232366A1",
            "publicationDate":"2021-07-29 00:00:00",
            "type":"Utility",
            "url":"https://patentimages.storage.googleapis.com/33/ed/0c/0b6b6f87e55fea/US20210232366A1.pdf"
       },
       {
            "applicationNumber":"17162550",
            "companyFilingName":[
                 "NVIDIA CORPORATION"
            ],
            "description":"REAL-TIME HARDWARE-ASSISTED GPU TUNING USING MACHINE LEARNING",
            "filingDate":"2021-01-29 00:00:00",
            "filingStatus":"Application",
            "patentNumber":"US20210174569A1",
            "publicationDate":"2021-06-10 00:00:00",
            "type":"Utility",
            "url":"https://patentimages.storage.googleapis.com/23/40/45/98b27a921d657c/US20210174569A1.pdf"
       }

   ],
   "symbol":"NVDA"
}
```

## H1-B Visa Application (Free)

Python client: `finnhub_client.stock_visa_application(...)`

Get a list of H1-B and Permanent visa applications for companies from the DOL. The data is updated quarterly.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

from REQUIRED . Filter on the column.
From date column.

to REQUIRED . Filter on the
To date

**Response Attributes:**

data
Array of H1b and Permanent visa applications.

beginDate
Job's start date.

caseNumber
Case number.

caseStatus
Case status.

employerName
Company's name.

endDate
Job's end date.

fullTimePosition
Full-time position flag.

h1bDependent
H1B dependent flag.

jobTitle
Job Title.

quarter
Quarter.

receivedDate
Received date.

socCode
SOC Code. A list of SOC code can be found here.

symbol
Symbol.

visaClass
Visa class.

wageLevel

Wage level.

wageRangeFrom
Wage range from.

wageRangeTo
Wage range to.

wageUnitOfPay
Wage unit of pay.

worksiteAddress
Worksite address.

worksiteCity
Worksite city.

worksiteCounty
Worksite county.

worksitePostalCode
Worksite postal code.

worksiteState
Worksite state.

year
Year.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_visa_application("AAPL", "2021-01-01", "2022-06-15"))
```

Sample response:
```json
{
"data": [
       {
          "year": 2020,
          "quarter": 1,
          "symbol": "AAPL",
          "caseNumber": "I-200-19268-472068",
          "caseStatus": "Certified",
          "receivedDate": "2019-09-25",
         "visaClass": "H-1B",
         "jobTitle": "ASIC DESIGN VERIFICATION ENGINEER",
         "socCode": "17-2072",
         "fullTimePosition": "Y",
         "beginDate": "2019-10-14",
         "endDate": "2022-10-13",
         "employerName": "APPLE INC.",
         "worksiteAddress": "320 S Capital of Texas Highway",
         "worksiteCity": "West Lake Hills",
         "worksiteCounty": "Travis",
         "worksiteState": "TX",
         "worksitePostalCode": "78746",
         "wageRangeFrom": 120000,
         "wageRangeTo": null,
         "wageUnitOfPay": "Year",
         "wageLevel": "II",
         "h1bDependent": "N"
      },
      ...
],
"symbol": "AAPL"
}
```

## Senate Lobbying (Free)

Python client: `finnhub_client.stock_lobbying(...)`

Get a list of reported lobbying activities in the Senate and the House.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data
Array of lobbying activities.

clientId
Client ID.

country
Country.

date
Date.

description

Description.

documentUrl
Document's URL.

expenses
Expenses reported by the company.

houseregistrantId
House registrant ID.

income
Income reported by lobbying firms.

name
Company's name.

period
Period.

postedName
Posted name.

registrantId
Registrant ID.

senateId
Senate ID.

symbol
Symbol.

year
Year.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_lobbying("AAPL", "2021-01-01", "2022-06-15"))
```

Sample response (truncated):
```json
{
"data":[
    {
       "symbol":"AAPL",
       "name":"APPLE, INC.",
       "description":"Hardware and software maunfacturer",
       "country":"US",
       "uuid":"db75bb6f-162a-433a-a997-a679eb4c6af6",
       "year":2020,
      "period":"fourth_quarter",
      "type":"Q4",
      "documentUrl":"https://lda.senate.gov/filings/public/filing/db75bb6f-162a-433a-a997-a679eb4c6af6/print/",
      "income":40000,
      "expenses":null,
      "postedName":"",
      "dtPosted":"",
      "clientId":"173094",
      "registrantId":"86196",
      "senateId":"86196-173094",
      "houseRegistrantId":"36548"
   },
   {
      "symbol":"AAPL",
      "name":"APPLE INC",
      "description":"",
      "country":"US",
      "uuid":"cad6db2f-c3ca-4b9d-bc24-4c56fc7eaadb",
      "year":2020,
      "period":"fourth_quarter",
      "type":"Q4",
      "documentUrl":"https://lda.senate.gov/filings/public/filing/cad6db2f-c3ca-4b9d-bc24-4c56fc7eaadb/print/",
      "income":null,
      "expenses":1450000,
      "postedName":"",
      "dtPosted":"",
      "clientId":"103979",
      "registrantId":"4152",
      "senateId":"4152-103979",
      "houseRegistrantId":"31450"
   }
...
```

## USA Spending (Free)

Python client: `finnhub_client.stock_usa_spending(...)`

Get a list of government's spending activities from USASpending dataset for public companies. This dataset can help you identify companies
that win big government contracts which is extremely important for industries such as Defense, Aerospace, and Education. Only recent data is
available via the API.

For historical data, you can download it here: Pre-2021, 2021, 2022, 2023, 2024

Arguments: . Filter for

symbol *(REQUIRED)*
Symbol.

from *(REQUIRED)*
From date

to REQUIRED . Filter for

To date

**Response Attributes:**

data
Array of government's spending data points.

actionDate
Period.

awardDescription
Description.

awardingAgencyName
Award agency.

awardingOfficeName
Award office name.

awardingSubAgencyName
Award sub-agency.

country
Recipient's country.

naicsCode
NAICS code.

performanceCity
Performance city.

performanceCongressionalDistrict
Performance congressional district.

performanceCountry
Performance country.

performanceCounty
Performance county.

performanceEndDate
Performance end date.

performanceStartDate
Performance start date.

performanceState
Performance state.

performanceZipCode
Performance zip code.

permalink
Permalink.

recipientName
Company's name.

recipientParentName
Company's name.

symbol
Symbol.

totalValue

Income reported by lobbying firms.

symbol
Symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_usa_spending("AAPL", "2021-01-01", "2022-06-15"))
```

Sample response:
```json
{
"data":[
       {
          "symbol":"AAPL",
          "recipientName":"APPLE INC.",
          "recipientParentName":"APPLE INC.",
          "country":"USA",
          "totalValue":4238,
          "actionDate":"2021-11-12",
         "performanceStartDate":"2021-11-12",
         "performanceEndDate":"2021-12-10",
         "awardingAgencyName":"SMITHSONIAN INSTITUTION (SI)",
         "awardingSubAgencyName":"SMITHSONIAN INSTITUTION",
         "awardingOfficeName":"SMITHSONIAN ASTROPHYSICAL OBSERVATORY",
         "performanceCountry":"USA",
         "performanceCity":"CUPERTINO",
         "performanceCounty":"SANTA CLARA",
         "performanceState":"CALIFORNIA",
         "performanceZipCode":"950140642",
         "performanceCongressionalDistrict":"17",
         "awardDescription":"MACBOOK PRO",
         "naicsCode":"334111",
         "permalink":"https://www.usaspending.gov/award/CONT_AWD_33131222P00465925_3300_-NONE-_-NONE-/"
      }
],
"symbol":"AAPL"
}
```

## Congressional Trading (Premium)

Python client: `finnhub_client.congressional_trading(...)`

Get stock trades data disclosed by members of congress.

**Arguments:**

symbol *(REQUIRED)*
Symbol of the company: AAPL.

from *(REQUIRED)*

From date .

to *(REQUIRED)*

To date .

**Response Attributes:**

data

Array of stock trades.

amountFrom
Transaction amount from.

amountTo
Transaction amount to.

assetName
Asset name.

filingDate
Filing date.

name
Name of the representative.

ownerType
Owner Type.

position
Position.

symbol
Symbol.

transactionDate
Transaction date.

transactionType

Transaction type or .

symbol
Symbol of the company.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.congressional_trading('AAPL', '2020-01-01', '2023-03-31'))
```

Sample response:
```json
{
"data": [
    {
       "amountFrom": 100001,
       "amountTo": 250000,
       "assetName": "Oppenheimer SteelPath MLP Select 40 Y (NASDAQ)",
       "filingDate": "2015-05-14",
       "name": "Lamar Alexander",
       "ownerType": "Spouse",
      "position": "senator",
      "symbol": "MLPTX",
      "transactionDate": "2014-04-04",
      "transactionType": "Purchase"
   },
   {
      "amountFrom": 1001,
      "amountTo": 15000,
      "assetName": "Oppenheimer SteelPath MLP Select 40 Y (NASDAQ)",
      "filingDate": "2015-05-14",
      "name": "Lamar Alexander",
      "ownerType": "Spouse",
      "position": "senator",
      "symbol": "MLPTX",
      "transactionDate": "2014-02-07",
      "transactionType": "Purchase"
   }
],
"symbol": "MLPTX"
}
```

## Bank Branch List (Premium)

Python client: `finnhub_client.bank_branch(...)`

Retrieve list of US bank branches information for a given symbol.
Premium: Accessible with Fundamental or All in One subscription.

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

data
Array of branches.
address
Branch address
branchId
Branch ID
date
Date opened
state
State
zipCode
Zip code

symbol

Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.bank_branch("JPM"))
```

Sample response:
```json
{
"data": [
    {
          "branchId": "201601",
          "address": "1910 E 95th St",
          "state": "IL",
          "zipCode": "60617",
          "date": "2000-02-28"
    },
   {
         "branchId": "359157",
         "address": "401 W 49th St",
         "state": "FL",
         "zipCode": "33012",
         "date": "2000-02-01"
   }
],
"symbol": "JPM"
}
```

## FDA Committee Meeting Calendar (Free)

Python client: `finnhub_client.fda_calendar(...)`

FDA's advisory committees are established to provide functions which support the agency's mission of protecting and promoting the public
health, while meeting the requirements set forth in the Federal Advisory Committee Act. Committees are either mandated by statute or
established at the discretion of the Department of Health and Human Services. Each committee is subject to renewal at two-year intervals
unless the committee charter states otherwise.

**Arguments:**

**Response Attributes:**

eventDescription
Event's description.

fromDate
Start time of the event in EST.

toDate
End time of the event in EST.

url
URL.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.fda_calendar())
```

Sample response:
```json
[
{
     "fromDate": "2016-01-11 19:00:00",
     "toDate": "2016-01-11 19:00:00",
     "eventDescription": "January 12, 2016: Meeting of the Psychopharmacologic Drugs Advisory Committee Meeting Announcement
- 01/11/2016 - 01/11/2016",
     "url": "https://www.fda.gov/advisory-committees/advisory-committee-calendar/january-12-2016-meeting-psychopharmacologic-
drugs-advisory-committee-meeting-announcement-01112016"
},
{
    "fromDate": "2016-01-14 13:00:00",
    "toDate": "2016-01-14 17:00:00",
    "eventDescription": "January 14, 2016: Vaccines and Related Biological Products Advisory Committee Meeting Announcement
- 01/14/2016 - 01/14/2016",
"url": "https://www.fda.gov/advisory-committees/advisory-committee-calendar/january-14-2016-vaccines-and-related-biological-
products-advisory-committee-meeting-announcement"
}
]
```

## AI Copilot (Premium)

Chat with our AI copilot trained on the extensive Finnhub's global data. You can ask it any finance-related questions just like with other LLM
models and receive results in texts and widgets.

Payload:

messages *(REQUIRED)*
Messages

stream *(optional)*
Stream responses

**Response Attributes:**

chatId
Chat ID.

content
Response text.

querySummary
Query summary

relatedQueries
Related queries.

sources
Sources.

tickers

List of tickers mentioned.

widgets
Widgets.

```python
import requests
import json
url = "https://finnhub.io/api/v1/ai-chat?token=YOUR_API_KEY"
payload = json.dumps({
     "messages": [
             {
                 "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": "What is the current price of NVDA?"
            }
       ]
})
response = requests.request("POST", url, data=payload)
print(response.json())
```

Sample response:
```json
{
"chatId": "uQElLdY7vZ",
"content": "The current price of NVIDIA Corp (NVDA) is $124.92. The price has increased by 3.97% in the past 24 hours.\n",
"querySummary": "NVDA Stock Price",
"relatedQueries": [
     "What is NVDA's price target?",
     "Is NVDA a good stock to buy?",
     "What factors affect NVDA's price?"
],
"sources": [
    {
       "link": "https://finnhub.io/docs/api",
       "shortURL": "finnhub.io",
       "snippet": "Comprehensive stock API for realtime market data, global company fundamentals, economic data, and
alternative data...",
       "title": "Finnhub API Documentation",
       "websiteName": "Finnhub"
    }
],
"tickers": [
    {
       "priceCurrency": "USD",
       "reportingCurrency": "USD",
       "ticker": "NVDA"
    }
],
"widgets": [
    "https://finnhub.io/widget?ticker=NVDA&which=historical-price"
]
}
```

## Revenue Breakdown & KPI (Premium)

Python client: `finnhub_client.stock_revenue_breakdown2(...)`

Get standardized revenue breakdown and KPIs data for 30,000+ global companies.

Premium: Premium

**Arguments:**

symbol *(REQUIRED)*
Symbol.

**Response Attributes:**

currency
currency
data
Revenue breakdown data.
symbol
Symbol

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.stock_revenue_breakdown2('AAPL'))
```

Sample response (truncated):
```json
{
"currency": "USD",
"data": {
    "annual": {
       "revenue_by_geography": [
          [
             {
                "data": [
                {
                   "period": "2023-09-30",
                   "value": 162560000000
               },
               {
                   "period": "2024-09-28",
                   "value": 167045000000
               }
               ],
               "label": "Americas"
            }
         ]
      ],
      "revenue_by_product": [
         [
            {
               "data": [
               {
                   "period": "2023-09-30",
                   "value": 200583000000
               },
               {
                   "period": "2024-09-28",
                   "value": 201183000000
               }
               ],
               "label": "iPhone"
            }
         ]
      ]
   },
   "quarterly": {
...
```

## Newsroom (Premium)

Python client: `finnhub_client.newsroom(...)`

Get latest articles posted directly on the companies' newsroom and investor relations page. Newsroom API along with the Press Releases API
provide a comprehensive text-based dataset directly from the company. We currently cover 1,250 US Companies with this dataset.

**Arguments:**

symbol *(REQUIRED)*
Company symbol.

from *(optional)*
From time: 2025-01-01.

to *(optional)*
To time: 2026-01-05.

**Response Attributes:**

data
Array of articles.

atDate format (EST timezone).
Published time in

fullText
URL to download the full text data.

title
Title.

url
Original URL.

symbol
Company symbol.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.newsroom('AAPL'))
```

Sample response:
```json
{
"data": [
      {
         "atDate": "2025-11-25 14:47:50",
         "fullText": "https://static2.finnhub.io/file/publicdatany/
newsroom_new/5def2b7215a5cae2334ad221236da9978f9eb20e737bcccc9080307f7df068ad.html.gz",
         "title": "AI at Work: Which future of jobs are we building toward?",
         "url": "https://www.microsoft.com/en-us/worklab/ai-at-work-which-future-of-jobs-are-we-building-towards"
      },
     {
        "atDate": "2025-11-20 05:50:57",
        "fullText": "https://static2.finnhub.io/file/publicdatany/
newsroom_new/36de40a2fc8c24227dd6fca77f7acc842bf4550ab7b51ab01a2fbecff250d2f2.html.gz",
        "title": "Why becoming an AI Frontier Firm is hard - Raffaella Sadun",
        "url": "https://www.microsoft.com/en-us/worklab/podcast/harvard-raffaella-sadun-on-why-its-so-hard-to-become-a-
frontier-firm"
     }
],
"symbol": "MSFT"
}
```

## International Filings (Premium)

Python client: `finnhub_client.international_filings(...)`

List filings for international companies. Limit to 500 documents at a time. These are the documents we use to source our fundamental data.
Enterprise clients who need access to the full filings for global markets should contact us for the access.

Premium: Access approved on a case by case basis

**Arguments:**

symbol *(optional)*
Symbol. Leave empty to list latest filings.

country *(optional)*
Filter by country using country's 2-letter code.

from *(optional)*
From date: 2023-01-15.

to *(optional)*
To date: 2023-12-16.

**Response Attributes:**

category
Category.

companyName
Company name.

country
Country.

description
Document's description.

filedDate

Filed date .

language

Language.

symbol
Symbol.

title
Document's title.

url
Url.

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.international_filings('AC.TO'))
```

Sample response:
```json
[
{
        "symbol": "MINDTREE.NS",
        "companyName": "MindTree Limited",
        "filedDate": "2015-03-31 20:27:00",
        "category": "Resignation of Director",
        "title": "MindTree Limited has informed the Exchange that Mr. David B Yoffie has resigned as Independent Director of the
company. The Board of Directors have accepted his resignation effective March 30, 2015.",
        "description": "",
       "url": "https://finnhub.io/international-filings?id=523566",
       "language": "en",
       "country": "IN"
},
{
       "symbol": "INOXLEISUR.NS",
       "companyName": "INOX Leisure Limited",
       "filedDate": "2015-03-31 20:24:00",
       "category": "Updates",
       "title": "INOX Leisure Limited has informed the Exchange regarding Commencement of Commercial Operations of Multiplex
Cinema Theatre situated at E-wing, Osia Commercial Arcade, SGPDA Market Complex, Margao, Goa 403601.",
       "description": "",
       "url": "https://finnhub.io/international-filings?id=52152",
       "language": "en",
       "country": "IN"
}
]
```

## Global Filings Search (Premium)

Search for best-matched filings across global companies' filings, transcripts and press releases. You can filter by anything from symbol, ISIN to
form type, and document sources.

This endpoint will return a list of documents that match your search criteria. If you would like to get the excerpts as well, please set

to . Once you have the list of documents, you can get a list of excerpts and positions to highlight the document using the

endpoint

Payload: endpoint to see all available values.

acts *(optional)*

List of SEC's exchanges act to search, comma separated. Look at

caps optional endpoint to see all available values.
List of market capitalization to search, comma separated. Look at

chIds *(optional)*
List of Companies House number to search, comma separated (Max: 50).

ciks *(optional)*
List of SEC Center Index Key to search, comma separated (Max: 50).

countries optional endpoint to see all available values.
List of sources to search, comma separated (Max: 50). Look at

cusips *(optional)*
List of cusip to search, comma separated (Max: 50).

exchanges optional endpoint to see all available values.
List of exchanges to search, comma separated (Max: 50). Look at

exhibits optional endpoint to see all available values.
List of exhibits to search, comma separated (Max: 50). Look at

forms optional endpoint to see all available values.
List of forms to search, comma separated (Max: 50). Look at

fromDate *(optional)*
Search from date in format: YYYY-MM-DD, default from the last 2 years

gics optional endpoint to see all available values.
List of gics to search, comma separated (Max: 50). Look at

highlighted *(optional)*
Enable highlight in returned filings. If enabled, only return 10 results each time

isins *(optional)*
List of isin to search, comma separated (Max: 50).

naics optional endpoint to see all available values.
List of sources to search, comma separated (Max: 50). Look at

page *(optional)*
Use for pagination, default to page 1

query *(REQUIRED)*
Search query

sedarIds *(optional)*
List of SEDAR issuer number to search, comma separated (Max: 50).

sedols *(optional)*
List of sedols to search, comma separated (Max: 50).

sort optional endpoint to see all available values.
Sort result by, default: sortMostRecent. Look at

sources optional endpoint to see all available values.
List of sources to search, comma separated (Max: 50). Look at

symbols *(optional)*

List of symbols to search, comma separated (Max: 50).

toDate *(optional)*
Search to date in format: YYYY-MM-DD, default to today

**Response Attributes:**

count
Total filing matched your search criteria.
filings
Filing match your search criteria.
acceptanceDate
Date the filing is submitted.
amend
Amendment
documentCount
Number of document in this filing
filedDate
Date the filing is made available to the public
filerId
Id of the entity submitted the filing
filingId
Filing Id in Alpharesearch platform
form
Filing Form
name
Filer name
pageCount
Estimate number of page when printing
reportDate
Date as which the filing is reported
source
Filing Source
symbol
List of symbol associate with this filing
title
Filing title
page
Current search page
took
Time took to execute your search query on our server, value in ms.

```python
import requests
import json
url = "https://finnhub.io/api/v1/global-filings/search?token=YOUR_API_KEY"
payload = json.dumps({
"query": "artificial intelligence",
"symbols": "AAPL,GOOGL,TSLA",
"fromDate": "2010-01-01",
"toDate": "2022-09-30"
})
response = requests.request("POST", url, data=payload)
print(response.json())
```

Sample response:
```json
{    "count": 8,
    "filings": [

          {
                 "acceptanceDate": "2022-10-27 00:00:00",
                 "amend": false,
                 "documentCount": 1,
                 "filedDate": "2022-10-27",
                 "filerId": "3285503214",
                "filingId": "AAPL_1113753",
                "form": "TR/E",
                "name": "Apple Inc",
                "pageCount": 4,
                "reportPeriod": "",
                "source": "TR",
                "symbols": [
                       "AAPL"
                ],
                "title": "AAPL - Earnings call Q4 2022",
                "url": "https://alpharesearch.io/platform/share?filingId=AAPL_1113753"

         }
         ...
   ],
   "page": 1,
}  "took": 1986
```

## Search In Filing (Premium)

Get a list of excerpts and highlight positions within a document using your query.

Payload:
filingId *(REQUIRED)*
Filing Id to search
query *(REQUIRED)*
Search query

**Response Attributes:**

acceptanceDate
Date the filing is submitted.

amend
Amendment

documentCount
Number of document in this filing

documents
Document for this filing.

documentId
AlphaResearch internal document id.

excerpts
Highlighted excerpts for this document

content
Highlighted content

endOffset
End offset of highlighted content

snippetId
Location of the content in the rendered document

startOffset
Start offset of highlighted content

format
Format of this document (can be html or pdf)

hits
Number of hit in this document

title
Title for this document.

url
Link to render this document

filedDate
Date the filing is make available to the public

filerId
Id of the entity submitted the filing

filingId
Filing Id in Alpharesearch platform

form
Filing Form

name
Filer name

pageCount
Estimate number of page when printing

reportDate
Date as which the filing is reported

source
Filing Source

symbol

List of symbol associate with this filing

title
Filing title

```python
import requests
import json
url = "https://finnhub.io/api/v1/global-filings/search-in-filing?token=YOUR_API_KEY"
payload = json.dumps({
"query": "covid",
"filingId": "AAPL_1113753"
})
response = requests.request("POST", url, data=payload)
print(response.json())
```

Sample response:
```json
{
"acceptanceDate": "2022-10-27 00:00:00",
"amend": false,
"documentCount": 1,
"documents": [
          {
                "documentId": "AAPL_1113753",
                "excerpts": [
                    {
                        "content": "If you compare it to pre-<span class='search-highlight'>pandemic</span> kind of levels, that
has not returned to pre <span class='search-highlight'>pandemic</span> levels by any means.\n",
                        "endOffset": 494,
                        "snippetId": "tran-46",
                        "startOffset": 385
                   }
                   ...
               ],
               "format": "html",
               "hits": 5,
               "title": "Transcript",
               "url": "https://alpharesearch.io/filing/transcript?documentId=AAPL_1113753"
         }
],
"filedDate": "2022-10-27",
"filerId": "4295905573",
"filingId": "AAPL_1113753",
"form": "TR/E",
"name": "Apple Inc",
"pageCount": 4,
"reportPeriod": "",
"source": "TR",
"symbols": [
         "AAPL"
],
"title": "AAPL - Earnings call Q4 2022",
"url": "https://alpharesearch.io/platform/share?filingId=AAPL_1113753"
}
```

## Search Filter (Premium)

Get available values for each filter in search body.

**Arguments:**

field *(REQUIRED)*
Field to get available filters. Available filters are "countries", "exchanges", "exhibits", "forms", "gics", "naics", "caps", "acts", and "sort".

source *(optional)*
Get available forms for each source.

**Response Attributes:**

id
Filter id, use with respective field in search query body.

name
Display name.

```python
import requests
url = "https://finnhub.io/api/v1/global-filings/filter?field=sources&token=YOUR_API_KEY"
response = requests.request("GET", url)
print(response.json())
```

Sample response:
```json
[    {
          "id": "SEC",
          "name": "US SEC Edgar Filings"

    },
    {

          "id": "TR",
          "name": "Event Transcripts"
   },
   {
         "id": "SEDAR",
         "name": "Canada SEDAR Filings"
   },
   {
         "id": "CH",
         "name": "UK Companies House Filings"
   },
   {
         "id": "PR",
         "name": "Press Releases"
   },
   {
         "id": "RR",
         "name": "Research Reports"
   },
   {
         "id": "GF",
         "name": "Global Filings"
]  }
```

## Download Filings (Premium)

Download filings using document ids.

**Arguments:**

documentId *(REQUIRED)*
Document's id. Note that this is different from filingId as 1 filing can contain multiple documents.

```python
import requests
url = "https://finnhub.io/api/v1/global-filings/download?
documentId=AAPL_1113753&token=YOUR_API_KEY"
response = requests.request("GET", url)
print(response.json())
```

## Country Metadata (Free)

Python client: `finnhub_client.country(...)`

List all countries and metadata.

**Arguments:**

**Response Attributes:**

code2
Alpha 2 code
code3
Alpha 3 code
codeNo
UN code
country
Country name
countryRiskPremium
Country risk premium
currency
Currency name

currencyCode

Currency code

defaultSpread
Default spread

equityRiskPremium
Equity risk premium

logo
Flag image

rating
Credit rating.

region
Region

subRegion
Sub-Region

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.country())
```

Sample response:
```json
[
{
    "code2": "US",
    "code3": "USA",
    "codeNo": "840",
    "country": "United States",
    "countryRiskPremium": 0,
    "currency": "US Dollar",
    "currencyCode": "USD",
   "defaultSpread": 0,
   "equityRiskPremium": 5,
   "region": "Americas",
   "subRegion": "Northern America",
   "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/country_logo/us.svg"
},
{
   "code2": "GB",
   "code3": "GBR",
   "codeNo": "826",
   "country": "United Kingdom of Great Britain and Northern Ireland",
   "countryRiskPremium": 0.91,
   "currency": "Sterling",
   "currencyCode": "GBP",
   "defaultSpread": 0.64,
   "equityRiskPremium": 5.91,
   "region": "Europe",
   "subRegion": "Northern Europe",
   "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/country_logo/gb.svg"
}
]
```

## Economic Calendar (Premium)

Python client: `finnhub_client.calendar_economic(...)`

Get recent and upcoming economic releases.
Historical events and surprises are available for Enterprise clients.

**Arguments:**

from *(optional)*

From date .

to *(optional)*

To date .

**Response Attributes:**

economicCalendar
Array of economic events.

actual
Actual release

country
Country

estimate
Estimate

event
Event

impact
Impact level

prev
Previous release

time
Release time

unit
Unit

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.calendar_economic())
```

Sample response:
```json
{
"economicCalendar": [
    {
       "actual": 8.4,
       "country": "AU",
       "estimate": 6.9,
       "event": "Australia - Current Account Balance",
       "impact": "low",
       "prev": 1,
      "time": "2020-06-02 01:30:00",
      "unit": "AUD"
   },
   {
      "actual": 0.5,
      "country": "AU",
      "estimate": 0.4,
      "event": "Australia- Net Exports",
      "impact": "low",
      "prev": -0.1,
      "time": "2020-06-02 01:30:00",
      "unit": "%"
   }
]
}
```

## Economic Code (Premium)

Python client: `finnhub_client.economic_code(...)`

List codes of supported economic data.
Premium: Accessible with Fundamental data or All in One subscription.

**Arguments:**

**Response Attributes:**

code
Finnhub economic code used to get historical data
country
Country
name
Indicator name
unit
Unit

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.economic_code())
```

Sample response:
```json
[
{
              "code": "MA-USA-656880",
              "country": "USA",
              "name": "1-Day Repo Rate",
              "unit": "%"
},
{
              "code": "MA-USA-6667797870",
             "country": "USA",
             "name": "ISM Purchasing Managers Index",
             "unit": "unit"
}
]
```

## Economic Data (Premium)

Python client: `finnhub_client.economic_data(...)`

Get economic data.

Premium: Accessible with Fundamental data or All in One subscription.

**Arguments:**

code *(REQUIRED)*
Economic code.

**Response Attributes:**

code
Finnhub economic code

data
Array of economic data for requested code.

date
Date of the reading

value
Value

```python
import finnhub
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
print(finnhub_client.economic_data('MA-USA-656880'))
```

Sample response:
```json
{
"code": "MA-USA-656880",
"data": [
    {
       "date": "2020-05-31",
       "value": -2760
    },
    {
       "date": "2020-04-30",
      "value": -19557
   }
]
}
```

