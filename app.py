from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
GE_TAX_RATE = 0.02
GE_TAX_CAP = 5_000_000
DEFAULT_USER_AGENT = "OSRS-GE-Flipper public Streamlit app / contact: replace-with-your-email"

st.set_page_config(page_title="OSRS GE Flipper", page_icon="💰", layout="wide")

TEXT = {
    "LT": {
        "title": "💰 Plebcity",
        "caption": "Paprastesnis flipping scanneris: buy/sell, profit, volume, rizika, kainos kreivė ir rinkos pulsas.",
        "filters": "Filtrai",
        "language": "Kalba / Language",
        "bankroll": "Tavo bankroll GP",
        "simple_mode": "Saugus režimas / mažiau rizikos",
        "simple_mode_help": "Įjungus rodo tik šviežesnius, aktyvesnius ir patikimesnius itemus.",
        "min_volume": "Min 1h volume",
        "min_5m_volume": "Min 5m volume",
        "min_profit": "Min profit / item",
        "min_roi": "Min ROI %",
        "min_conf": "Min patikimumas",
        "max_age": "Max pask. trade amžius, min",
        "min_buy": "Min buy price",
        "max_buy": "Max buy price",
        "members_filter": "Members filtras",
        "all": "Visi",
        "members_only": "Members only",
        "f2p_only": "F2P only",
        "search": "Ieškoti itemo",
        "sort_by": "Rūšiuoti pagal",
        "top_n": "Kiek rodyti",
        "auto_refresh": "Automatiškai atnaujinti",
        "refresh_seconds": "Atnaujinimo intervalas",
        "refresh": "Atnaujinti dabar",
        "advanced": "Advanced",
        "loading": "Kraunami GE duomenys...",
        "load_error": "Nepavyko užkrauti OSRS kainų duomenų",
        "recommended": "Rekomenduojami flipai",
        "details": "Pilna lentelė",
        "charts": "Kainos kreivė",
        "market_pulse": "Rinkos pulsas",
        "most_bought": "Daugiausiai perkami 1h",
        "most_sold": "Daugiausiai parduodami 1h",
        "buy_pressure": "Stipriausias pirkimo spaudimas",
        "sell_pressure": "Stipriausias pardavimo spaudimas",
        "pulse_help": "Čia rodoma, kur šiuo metu daugiausia aktyvumo ir disbalanso pagal 1h high/low volume.",
        "bought": "Nupirkta",
        "sold": "Parduota",
        "pressure": "Spaudimas",
        "signal": "Signalas",
        "ai_note": "AI pastaba",
        "demand_buy": "Buy pressure",
        "demand_sell": "Sell pressure",
        "demand_neutral": "Neutralu",
        "how_to": "Kaip naudoti ir mažinti riziką",
        "download": "Atsisiųsti CSV",
        "candidates": "Rasta",
        "best_profit": "Best profit/item",
        "best_roi": "Best ROI",
        "avg_conf": "Vid. patikimumas",
        "item": "Itemas",
        "buy": "Pirkti apie",
        "sell": "Parduoti apie",
        "profit": "Profit/item",
        "roi": "ROI",
        "vol": "1h volume",
        "bs_1h": "Nupirkta / parduota 1h",
        "conf": "Patikimumas",
        "risk": "Rizika",
        "change": "Pokytis",
        "limit": "Limit",
        "qty": "Kiek pirkti",
        "bank_profit": "Profit su bankroll",
        "tax": "GE tax",
        "last_trade": "Pask. trade",
        "momentum": "Momentum",
        "score": "Score",
        "high": "Aukštas",
        "medium": "Vidutinis",
        "low": "Žemas",
        "risk_low": "Maža",
        "risk_medium": "Vidutinė",
        "risk_high": "Didelė",
        "chart_item": "Pasirink itemą",
        "chart_period": "Laikotarpis",
        "chart_type": "Kaina",
        "mid_price": "Vidurkis",
        "high_price": "High / sell",
        "low_price": "Low / buy",
        "empty": "Pagal šiuos filtrus nieko nerasta. Pabandyk sumažinti min volume, min confidence arba min profit.",
        "warning": "Tai nėra garantuotas pelnas. Buy/sell yra target zona pagal paskutinius low/high sandorius.",
        "risk_md": """
### Rizikos mažinimo taisyklės

1. **Pradėk nuo mažesnio kiekio** — nepirk iškart viso limit. Pirma pabandyk 5–20% limit.
2. **Rinkis didesnį volume** — jeigu 1h volume mažas, flipas gali užstrigti.
3. **Venk senų kainų** — jeigu paskutinis trade senas, spread gali būti netikras.
4. **Žiūrėk patikimumą** — saugesniems flipams naudok 70+ confidence.
5. **Nežiūrėk tik į profitą** — didelis profit su mažu volume dažnai yra spąstai.
6. **Nekelk kainos agresyviai** — jeigu nepirksta, kelk po truputį, ne iškart daug.
7. **Brangiems itemams naudok mažesnę bankroll dalį** — ne daugiau kaip 10–25% bankroll į vieną itemą.

**Saugus režimas** automatiškai bando palikti tik aktyvesnius, šviežesnius ir stabilesnius itemus.
""",
    },
    "EN": {
        "title": "💰 OSRS GE Flipper",
        "caption": "Simpler flipping scanner: buy/sell targets, profit, volume, risk, price curve and market pulse.",
        "filters": "Filters",
        "language": "Language / Kalba",
        "bankroll": "Your bankroll GP",
        "simple_mode": "Safe mode / lower risk",
        "simple_mode_help": "When enabled, shows fresher, more active and higher-confidence items.",
        "min_volume": "Min 1h volume",
        "min_5m_volume": "Min 5m volume",
        "min_profit": "Min profit / item",
        "min_roi": "Min ROI %",
        "min_conf": "Min confidence",
        "max_age": "Max last trade age, min",
        "min_buy": "Min buy price",
        "max_buy": "Max buy price",
        "members_filter": "Members filter",
        "all": "All",
        "members_only": "Members only",
        "f2p_only": "F2P only",
        "search": "Search item",
        "sort_by": "Sort by",
        "top_n": "Rows to show",
        "auto_refresh": "Auto refresh",
        "refresh_seconds": "Refresh interval",
        "refresh": "Refresh now",
        "advanced": "Advanced",
        "loading": "Loading GE data...",
        "load_error": "Could not load OSRS price data",
        "recommended": "Recommended flips",
        "details": "Full table",
        "charts": "Price curve",
        "market_pulse": "Market Pulse",
        "most_bought": "Most bought 1h",
        "most_sold": "Most sold 1h",
        "buy_pressure": "Strongest buy pressure",
        "sell_pressure": "Strongest sell pressure",
        "pulse_help": "Shows where current activity and imbalance are highest based on 1h high/low volume.",
        "bought": "Bought",
        "sold": "Sold",
        "pressure": "Pressure",
        "signal": "Signal",
        "ai_note": "AI note",
        "demand_buy": "Buy pressure",
        "demand_sell": "Sell pressure",
        "demand_neutral": "Neutral",
        "how_to": "How to use and lower risk",
        "download": "Download CSV",
        "candidates": "Found",
        "best_profit": "Best profit/item",
        "best_roi": "Best ROI",
        "avg_conf": "Avg confidence",
        "item": "Item",
        "buy": "Buy near",
        "sell": "Sell near",
        "profit": "Profit/item",
        "roi": "ROI",
        "vol": "1h volume",
        "bs_1h": "Bought / sold 1h",
        "conf": "Confidence",
        "risk": "Risk",
        "change": "Change",
        "limit": "Limit",
        "qty": "Qty to buy",
        "bank_profit": "Profit with bankroll",
        "tax": "GE tax",
        "last_trade": "Last trade",
        "momentum": "Momentum",
        "score": "Score",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "risk_low": "Low",
        "risk_medium": "Medium",
        "risk_high": "High",
        "chart_item": "Choose item",
        "chart_period": "Timeframe",
        "chart_type": "Price",
        "mid_price": "Average",
        "high_price": "High / sell",
        "low_price": "Low / buy",
        "empty": "No items match these filters. Try lowering min volume, min confidence or min profit.",
        "warning": "This is not guaranteed profit. Buy/sell are target zones based on recent low/high trades.",
        "risk_md": """
### Lower-risk flipping rules

1. **Start with a smaller quantity** — do not buy the whole limit immediately. Test 5–20% first.
2. **Prefer higher volume** — low 1h volume can trap your GP for a long time.
3. **Avoid stale prices** — old last trades can mean the spread is fake.
4. **Use confidence** — for safer flips, use 70+ confidence.
5. **Do not chase profit only** — high profit with low volume is often a trap.
6. **Adjust prices slowly** — if orders do not fill, adjust gradually, not aggressively.
7. **Limit exposure on expensive items** — avoid putting more than 10–25% bankroll into one item.

**Safe mode** automatically tries to keep only more active, fresher and more stable items.
""",
    },
}


def ge_tax(sell_price: int) -> int:
    if sell_price <= 0:
        return 0
    return min(int(sell_price * GE_TAX_RATE), GE_TAX_CAP)


@st.cache_data(ttl=60, show_spinner=False)
def get_json(endpoint: str, user_agent: str) -> dict:
    r = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"User-Agent": user_agent or DEFAULT_USER_AGENT},
        timeout=25,
    )
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=3600, show_spinner=False)
def load_mapping(user_agent: str) -> pd.DataFrame:
    rows = []
    for item in get_json("mapping", user_agent):
        rows.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "limit": item.get("limit"),
            "members": item.get("members"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60, show_spinner=False)
def load_latest(user_agent: str) -> pd.DataFrame:
    rows = []
    for item_id, price in get_json("latest", user_agent).get("data", {}).items():
        low = price.get("low")
        high = price.get("high")
        if low is None or high is None or low <= 0 or high <= 0:
            continue
        rows.append({
            "id": int(item_id),
            "buy_price": int(low),
            "sell_price": int(high),
            "raw_margin": int(high) - int(low),
            "low_time": price.get("lowTime"),
            "high_time": price.get("highTime"),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300, show_spinner=False)
def load_period(period: str, user_agent: str) -> pd.DataFrame:
    rows = []
    for item_id, price in get_json(period, user_agent).get("data", {}).items():
        rows.append({
            "id": int(item_id),
            f"avg_high_{period}": price.get("avgHighPrice"),
            f"avg_low_{period}": price.get("avgLowPrice"),
            f"bought_{period}": price.get("highPriceVolume", 0) or 0,
            f"sold_{period}": price.get("lowPriceVolume", 0) or 0,
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300, show_spinner=False)
def load_timeseries(item_id: int, timestep: str, user_agent: str) -> pd.DataFrame:
    data = get_json(f"timeseries?timestep={timestep}&id={item_id}", user_agent).get("data", [])
    rows = []
    for p in data:
        hi = p.get("avgHighPrice")
        lo = p.get("avgLowPrice")
        if hi is None and lo is None:
            continue
        mid = (hi + lo) / 2 if hi is not None and lo is not None else hi if hi is not None else lo
        rows.append({
            "time": pd.to_datetime(p.get("timestamp"), unit="s", utc=True, errors="coerce"),
            "high": hi,
            "low": lo,
            "mid": mid,
            "volume": (p.get("highPriceVolume") or 0) + (p.get("lowPriceVolume") or 0),
        })
    return pd.DataFrame(rows).dropna(subset=["time"]).sort_values("time")


def build_flips(user_agent: str, bankroll_gp: int) -> pd.DataFrame:
    mapping = load_mapping(user_agent)
    latest = load_latest(user_agent)
    five = load_period("5m", user_agent)
    hour = load_period("1h", user_agent)

    df = latest.merge(mapping, on="id", how="left").merge(five, on="id", how="left").merge(hour, on="id", how="left")
    df["limit"] = df["limit"].fillna(1).astype(int)
    for c in ["bought_5m", "sold_5m", "bought_1h", "sold_1h"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["volume_5m"] = df["bought_5m"] + df["sold_5m"]
    df["volume_1h"] = df["bought_1h"] + df["sold_1h"]

    df["tax"] = df["sell_price"].apply(ge_tax)
    df["profit_per_item"] = df["sell_price"] - df["tax"] - df["buy_price"]
    df["roi_percent"] = (df["profit_per_item"] / df["buy_price"]) * 100
    df["affordable_qty"] = (bankroll_gp // df["buy_price"]).astype(int)
    df["flip_qty"] = df[["limit", "affordable_qty"]].min(axis=1)
    df["profit_with_bankroll"] = df["profit_per_item"] * df["flip_qty"]

    for c in ["avg_high_5m", "avg_low_5m", "avg_high_1h", "avg_low_1h"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["momentum_percent"] = ((df["avg_high_5m"] - df["avg_high_1h"]) / df["avg_high_1h"]) * 100
    df["current_mid_price"] = (df["buy_price"] + df["sell_price"]) / 2
    df["avg_mid_1h"] = (df["avg_high_1h"] + df["avg_low_1h"]) / 2
    df["price_change_percent"] = ((df["current_mid_price"] - df["avg_mid_1h"]) / df["avg_mid_1h"]) * 100
    df["recent_profit_per_item"] = df["avg_high_5m"] - df["avg_low_5m"] - df["avg_high_5m"].fillna(0).apply(lambda x: ge_tax(int(x)) if x > 0 else 0)

    df["last_high_trade"] = pd.to_datetime(df["high_time"], unit="s", utc=True, errors="coerce")
    df["last_low_trade"] = pd.to_datetime(df["low_time"], unit="s", utc=True, errors="coerce")
    df["last_trade_time"] = df[["last_high_trade", "last_low_trade"]].max(axis=1)
    now = pd.Timestamp.now(tz="UTC")
    df["minutes_since_trade"] = ((now - df["last_trade_time"]).dt.total_seconds() / 60).fillna(9999)

    df["confidence_score"] = (
        np.minimum(df["volume_1h"] / 2500, 1) * 24
        + np.minimum(df["volume_5m"] / 250, 1) * 18
        + np.where(df["profit_per_item"] > 0, 13, 0)
        + np.minimum(df["roi_percent"].clip(lower=0) / 2.5, 1) * 13
        + np.where(df["minutes_since_trade"] <= 10, 17, np.where(df["minutes_since_trade"] <= 30, 10, np.where(df["minutes_since_trade"] <= 60, 5, 0)))
        + np.where(df["recent_profit_per_item"] > 0, 15, 0)
    ).round().astype(int).clip(0, 100)

    df["risk_score"] = 100 - df["confidence_score"]
    df.loc[df["volume_1h"] < 100, "risk_score"] += 15
    df.loc[df["minutes_since_trade"] > 60, "risk_score"] += 15
    df.loc[df["recent_profit_per_item"] <= 0, "risk_score"] += 15
    df["risk_score"] = df["risk_score"].clip(0, 100)

    df["flip_score"] = (
        df["confidence_score"] * 6
        + df["profit_per_item"].clip(lower=0) * 0.25
        + df["roi_percent"].clip(lower=0) * 15
        + df["volume_1h"].clip(upper=15000) * 0.01
    )
    return df


def rs_num(value, suffix=""):
    try:
        n = float(value)
    except Exception:
        return f"0{suffix}"
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        s = f"{n/1_000_000_000:.2f}".rstrip("0").rstrip(".") + "B"
    elif n >= 1_000_000:
        s = f"{n/1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    elif n >= 100_000:
        s = f"{n/1_000:.0f}K"
    elif n >= 10_000:
        s = f"{n/1_000:.1f}".rstrip("0").rstrip(".") + "K"
    else:
        s = f"{n:,.0f}"
    return f"{sign}{s}{suffix}"


def gp(value):
    return rs_num(value, " gp")


def pct(value):
    return "n/a" if pd.isna(value) else f"{value:.2f}%"


def mins(value):
    if pd.isna(value) or value > 9000:
        return "n/a"
    return f"{value:.0f}m"


def color_num(value):
    try:
        n = float(value)
    except Exception:
        return ""
    if n > 0:
        return "color:#16a34a;font-weight:700"
    if n < 0:
        return "color:#dc2626;font-weight:700"
    return "color:#6b7280"


def color_conf(value):
    txt = str(value).lower()
    if "high" in txt or "aukšt" in txt:
        return "color:#16a34a;font-weight:700"
    if "medium" in txt or "vidut" in txt:
        return "color:#ca8a04;font-weight:700"
    if "low" in txt or "žem" in txt or "didel" in txt:
        return "color:#dc2626;font-weight:700"
    return ""


def pressure_label(value, t):
    try:
        v = float(value)
    except Exception:
        return t["demand_neutral"]
    if v >= 25:
        return "🟢 " + t["demand_buy"]
    if v <= -25:
        return "🔴 " + t["demand_sell"]
    return "🟡 " + t["demand_neutral"]


def ai_market_note(row, lang):
    pressure = row.get("buy_pressure_percent", 0)
    vol = row.get("volume_1h", 0)
    change = row.get("price_change_percent", 0)
    profit = row.get("profit_per_item", 0)
    conf = row.get("confidence_score", 0)
    if lang == "LT":
        if vol < 100:
            return "Mažas volume — atsargiai, orderiai gali ilgai stovėti."
        if pressure >= 35 and change > 0:
            return "Daug perka ir kaina kyla — stebėti momentum, bet nepirkti per aukštai."
        if pressure >= 35 and profit > 0 and conf >= 65:
            return "Stipri paklausa + teigiamas margin — galimas greitesnis flipas."
        if pressure <= -35 and change < 0:
            return "Daug parduoda ir kaina krenta — didesnė crash rizika."
        if pressure <= -35:
            return "Pardavimo spaudimas — geriau laukti žemesnės buy kainos."
        if profit > 0 and conf >= 70:
            return "Subalansuotas aktyvumas ir aukštas patikimumas — saugesnis kandidatas."
        return "Neutralus signalas — tikrinti volume, spread ir paskutinio trade amžių."
    else:
        if vol < 100:
            return "Low volume — be careful, orders may sit for a long time."
        if pressure >= 35 and change > 0:
            return "Heavy buying and price rising — watch momentum, avoid overpaying."
        if pressure >= 35 and profit > 0 and conf >= 65:
            return "Strong demand + positive margin — possible faster flip."
        if pressure <= -35 and change < 0:
            return "Heavy selling and price falling — higher crash risk."
        if pressure <= -35:
            return "Sell pressure — better to wait for a lower buy price."
        if profit > 0 and conf >= 70:
            return "Balanced activity and high confidence — safer candidate."
        return "Neutral signal — check volume, spread and last trade age."


def row_tint(row):
    val = row.get("price_change_percent", 0)
    try:
        val = float(val)
    except Exception:
        val = 0
    if val > 0:
        return ["background-color:rgba(22,163,74,.07)"] * len(row)
    if val < 0:
        return ["background-color:rgba(220,38,38,.07)"] * len(row)
    return [""] * len(row)


with st.sidebar:
    lang = st.selectbox("Kalba / Language", ["LT", "EN"], index=0)

t = TEXT[lang]
st.title(t["title"])
st.caption(t["caption"])

with st.sidebar:
    st.header(t["filters"])
    bankroll_gp = st.number_input(t["bankroll"], min_value=1_000, max_value=10_000_000_000, value=10_000_000, step=100_000)
    safe_mode = st.checkbox(t["simple_mode"], value=True, help=t["simple_mode_help"])

    default_min_volume = 500 if safe_mode else 100
    default_min_5m = 50 if safe_mode else 0
    default_conf = 65 if safe_mode else 0
    default_age = 45 if safe_mode else 180
    default_profit = 10 if safe_mode else 5
    default_roi = 0.4 if safe_mode else 0.2

    min_volume_1h = st.number_input(t["min_volume"], min_value=0, value=default_min_volume, step=50)
    min_volume_5m = st.number_input(t["min_5m_volume"], min_value=0, value=default_min_5m, step=10)
    min_profit = st.number_input(t["min_profit"], min_value=-1_000_000, value=default_profit, step=5)
    min_roi = st.number_input(t["min_roi"], min_value=-100.0, value=default_roi, step=0.1)
    min_conf = st.slider(t["min_conf"], 0, 100, default_conf, 5)
    max_age = st.slider(t["max_age"], 5, 360, default_age, 5)
    min_buy = st.number_input(t["min_buy"], min_value=1, value=100, step=100)
    max_buy = st.number_input(t["max_buy"], min_value=1, value=50_000_000, step=100_000)

    members_filter = st.selectbox(t["members_filter"], [t["all"], t["members_only"], t["f2p_only"]])
    search = st.text_input(t["search"])
    sort_options = {
        "Confidence": "confidence_score",
        "Profit with bankroll": "profit_with_bankroll",
        "Profit / item": "profit_per_item",
        "ROI": "roi_percent",
        "Volume 1h": "volume_1h",
        "Score": "flip_score",
    }
    sort_label = st.selectbox(t["sort_by"], list(sort_options.keys()), index=0)
    top_n = st.slider(t["top_n"], 10, 200, 40, 10)

    auto_refresh = st.checkbox(t["auto_refresh"], value=True)
    refresh_seconds = st.selectbox(t["refresh_seconds"], [30, 60, 120, 300], index=1)

    with st.expander(t["advanced"]):
        user_agent = st.text_input("User-Agent", value=DEFAULT_USER_AGENT)

    if st.button(t["refresh"]):
        st.cache_data.clear()
        st.rerun()

if auto_refresh and st_autorefresh is not None:
    st_autorefresh(interval=int(refresh_seconds) * 1000, key="osrs_auto_refresh")

try:
    with st.spinner(t["loading"]):
        df = build_flips(user_agent, int(bankroll_gp))
except Exception as exc:
    st.error(f"{t['load_error']}: {exc}")
    st.stop()

f = df.copy()
f = f[f["volume_1h"] >= min_volume_1h]
f = f[f["volume_5m"] >= min_volume_5m]
f = f[f["profit_per_item"] >= min_profit]
f = f[f["roi_percent"] >= min_roi]
f = f[f["confidence_score"] >= min_conf]
f = f[f["minutes_since_trade"] <= max_age]
f = f[f["buy_price"] >= min_buy]
f = f[f["buy_price"] <= max_buy]
f = f[f["flip_qty"] > 0]
if safe_mode:
    f = f[f["recent_profit_per_item"] > 0]
    f = f[f["sell_price"] > f["buy_price"]]

if members_filter == t["members_only"]:
    f = f[f["members"] == True]
elif members_filter == t["f2p_only"]:
    f = f[f["members"] == False]

if search.strip():
    f = f[f["name"].str.contains(search.strip(), case=False, na=False)]

f = f.sort_values(sort_options[sort_label], ascending=False).head(top_n).copy()

if lang == "LT":
    f["confidence_label"] = np.select([f["confidence_score"] >= 70, f["confidence_score"] >= 45], [t["high"], t["medium"]], default=t["low"])
    f["risk_label"] = np.select([f["risk_score"] <= 35, f["risk_score"] <= 65], [t["risk_low"], t["risk_medium"]], default=t["risk_high"])
else:
    f["confidence_label"] = np.select([f["confidence_score"] >= 70, f["confidence_score"] >= 45], [t["high"], t["medium"]], default=t["low"])
    f["risk_label"] = np.select([f["risk_score"] <= 35, f["risk_score"] <= 65], [t["risk_low"], t["risk_medium"]], default=t["risk_high"])

f["bs_1h"] = f.apply(lambda r: f"{rs_num(r['bought_1h'])} / {rs_num(r['sold_1h'])}", axis=1)

# Market pulse uses a broader set than the main flip table, so it can show what people buy/sell even if it is not a safe flip.
market = df.copy()
if members_filter == t["members_only"]:
    market = market[market["members"] == True]
elif members_filter == t["f2p_only"]:
    market = market[market["members"] == False]
if search.strip():
    market = market[market["name"].str.contains(search.strip(), case=False, na=False)]
market = market[market["volume_1h"] > 0].copy()
market["buy_pressure_percent"] = ((market["bought_1h"] - market["sold_1h"]) / market["volume_1h"].replace(0, np.nan) * 100).fillna(0)
market["pressure_label"] = market["buy_pressure_percent"].apply(lambda v: pressure_label(v, t))
market["ai_note"] = market.apply(lambda r: ai_market_note(r, lang), axis=1)

c1, c2, c3, c4 = st.columns(4)
c1.metric(t["candidates"], f"{len(f):,}")
c2.metric(t["best_profit"], gp(f["profit_per_item"].max()) if not f.empty else "0 gp")
c3.metric(t["best_roi"], pct(f["roi_percent"].max()) if not f.empty else "0%")
c4.metric(t["avg_conf"], f"{f['confidence_score'].mean():.0f}/100" if not f.empty else "0/100")

tab1, tab2, tab3, tab4 = st.tabs([t["recommended"], t["market_pulse"], t["details"], t["charts"]])

simple_cols = [
    "name", "buy_price", "sell_price", "profit_per_item", "roi_percent", "bs_1h", "confidence_label", "risk_label"
]

with tab1:
    st.subheader(t["recommended"])
    if f.empty:
        st.info(t["empty"])
    else:
        simple = f[simple_cols].copy()
        styled = (
            simple.style
            .format({"buy_price": gp, "sell_price": gp, "profit_per_item": gp, "roi_percent": pct})
            .map(color_num, subset=["profit_per_item", "roi_percent"])
            .map(color_conf, subset=["confidence_label", "risk_label"])
        )
        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": t["item"],
                "buy_price": t["buy"],
                "sell_price": t["sell"],
                "profit_per_item": t["profit"],
                "roi_percent": t["roi"],
                "bs_1h": t["bs_1h"],
                "confidence_label": t["conf"],
                "risk_label": t["risk"],
            },
        )
    st.warning(t["warning"])

with tab2:
    st.subheader(t["market_pulse"])
    st.caption(t["pulse_help"])

    def market_table(data):
        cols = ["name", "bought_1h", "sold_1h", "volume_1h", "buy_pressure_percent", "price_change_percent", "pressure_label", "ai_note"]
        out = data[cols].head(25).copy()
        styled_market = (
            out.style
            .format({
                "bought_1h": rs_num, "sold_1h": rs_num, "volume_1h": rs_num,
                "buy_pressure_percent": pct, "price_change_percent": pct,
            })
            .map(color_num, subset=["buy_pressure_percent", "price_change_percent"])
            .map(color_conf, subset=["pressure_label"])
        )
        st.dataframe(
            styled_market,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": t["item"],
                "bought_1h": t["bought"],
                "sold_1h": t["sold"],
                "volume_1h": t["vol"],
                "buy_pressure_percent": t["pressure"],
                "price_change_percent": t["change"],
                "pressure_label": t["signal"],
                "ai_note": t["ai_note"],
            },
        )

    st.markdown("#### " + t["most_bought"])
    market_table(market.sort_values("bought_1h", ascending=False))

    st.markdown("#### " + t["most_sold"])
    market_table(market.sort_values("sold_1h", ascending=False))

    st.markdown("#### " + t["buy_pressure"])
    market_table(market[market["volume_1h"] >= max(100, min_volume_1h)].sort_values("buy_pressure_percent", ascending=False))

    st.markdown("#### " + t["sell_pressure"])
    market_table(market[market["volume_1h"] >= max(100, min_volume_1h)].sort_values("buy_pressure_percent", ascending=True))

with tab3:
    st.subheader(t["details"])
    if f.empty:
        st.info(t["empty"])
    else:
        detail_cols = [
            "name", "buy_price", "sell_price", "tax", "profit_per_item", "roi_percent", "price_change_percent",
            "confidence_score", "risk_score", "limit", "flip_qty", "profit_with_bankroll", "bought_5m", "sold_5m",
            "bought_1h", "sold_1h", "volume_5m", "volume_1h", "minutes_since_trade", "momentum_percent", "flip_score"
        ]
        detail = f[detail_cols].copy()
        styled_detail = (
            detail.style
            .format({
                "buy_price": gp, "sell_price": gp, "tax": gp, "profit_per_item": gp,
                "profit_with_bankroll": gp, "roi_percent": pct, "price_change_percent": pct,
                "momentum_percent": pct, "confidence_score": lambda v: f"{v:.0f}/100",
                "risk_score": lambda v: f"{v:.0f}/100", "limit": rs_num, "flip_qty": rs_num,
                "bought_5m": rs_num, "sold_5m": rs_num, "bought_1h": rs_num, "sold_1h": rs_num,
                "volume_5m": rs_num, "volume_1h": rs_num, "minutes_since_trade": mins,
                "flip_score": lambda v: f"{v:.1f}",
            })
            .apply(row_tint, axis=1)
            .map(color_num, subset=["profit_per_item", "roi_percent", "price_change_percent", "momentum_percent", "profit_with_bankroll"])
        )
        st.dataframe(
            styled_detail,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": t["item"],
                "buy_price": t["buy"],
                "sell_price": t["sell"],
                "tax": t["tax"],
                "profit_per_item": t["profit"],
                "roi_percent": t["roi"],
                "price_change_percent": t["change"],
                "confidence_score": t["conf"],
                "risk_score": t["risk"],
                "limit": t["limit"],
                "flip_qty": t["qty"],
                "profit_with_bankroll": t["bank_profit"],
                "minutes_since_trade": t["last_trade"],
                "momentum_percent": t["momentum"],
                "flip_score": t["score"],
            },
        )

with tab4:
    st.subheader(t["charts"])
    chart_options = f[["id", "name"]].drop_duplicates().head(250)
    if chart_options.empty:
        st.info(t["empty"])
        st.stop()
    name_to_id = dict(zip(chart_options["name"], chart_options["id"]))
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        selected_name = st.selectbox(t["chart_item"], list(name_to_id.keys()))
    with col_b:
        period_label = st.selectbox(t["chart_period"], ["24h / 5m", "7d / 1h", "30d / 6h", "1y / 24h"])
    with col_c:
        price_type = st.selectbox(t["chart_type"], [t["mid_price"], t["high_price"], t["low_price"]])

    timestep = period_label.split(" / ")[1]
    value_col = "mid"
    if price_type == t["high_price"]:
        value_col = "high"
    elif price_type == t["low_price"]:
        value_col = "low"

    try:
        ts = load_timeseries(int(name_to_id[selected_name]), timestep, user_agent)
        if ts.empty or ts[value_col].dropna().empty:
            st.info("No chart data for this item yet.")
        else:
            first = ts[value_col].dropna().iloc[0]
            last = ts[value_col].dropna().iloc[-1]
            change = ((last - first) / first) * 100 if first else 0
            color = "#16a34a" if change >= 0 else "#dc2626"
            st.metric(f"{selected_name} — {t['change']}", gp(last), delta=f"{change:.2f}%")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts["time"], y=ts[value_col], mode="lines", line=dict(color=color, width=3), hovertemplate="%{x}<br>%{y:,.0f} gp<extra></extra>"))
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Time", yaxis_title="GP", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"Chart could not load: {exc}")

csv = f.to_csv(index=False).encode("utf-8")
st.download_button(t["download"], data=csv, file_name=f"osrs_flips_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

with st.expander(t["how_to"], expanded=False):
    st.markdown(t["risk_md"])
